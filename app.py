import logging
import os  # ✅ os module imported for Render deploy
from flask import Flask, render_template, request
import pandas as pd
import joblib
from statistics import mean

predictions = []
logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("API_FOOTBALL_KEY")

# Dummy team stats setup
stat_cols = 16  # or however many your model expects

# Load model + encoders
model = joblib.load('model/model.pkl')
le_home = joblib.load('model/le_home.pkl')
le_away = joblib.load('model/le_away.pkl')

# Now that le_home is defined, this will work ✅
team_stats = {team: [0] * stat_cols for team in le_home.classes_}

app = Flask(__name__)

# Load model and data
model_bundle = joblib.load('model/model.pkl')
model = model_bundle['model']
le_home = model_bundle['home_encoder']
le_away = model_bundle['away_encoder']
history = pd.read_csv('data/E0.csv')

stat_cols = ['FTHG', 'FTAG', 'HTHG', 'HTAG',
             'HS', 'AS', 'HST', 'AST',
             'HF', 'AF', 'HC', 'AC',
             'HY', 'AY', 'HR', 'AR']
RECENT_MATCHES = 8

def get_recent_averages(team, is_home=True):
    if is_home:
        games = history[history['HomeTeam'] == team].tail(RECENT_MATCHES)
    else:
        games = history[history['AwayTeam'] == team].tail(RECENT_MATCHES)

    if games.empty:
        return [0] * len(stat_cols)  # Prevents the "mean requires at least one data point" error
    logging.info(f"Encoded teams: {list(le_home.classes_)}")
    return [games[col].fillna(0).mean() for col in stat_cols]

def predict_outcome(model, le_home, le_away, stat_cols, home, away, stats_dict):
    try:
        # 1. Gather statistical features for both teams
        home_stats = stats_dict.get(home)
        away_stats = stats_dict.get(away)

        if home_stats is None or away_stats is None:
            logging.error(f"Missing stats for {home} or {away}")
            return "Prediction Error ❌ (Unknown team)"

        # 2. Combine stats
        features = home_stats + away_stats  # 32 features total

        # 3. Encode team names as numerical values
        home_encoded = le_home.transform([home])[0]
        away_encoded = le_away.transform([away])[0]

        # 4. Append encoded team names to the feature vector
        features += [home_encoded, away_encoded]  # Now 34 features total

        # 5. Match the expected column order from training
        columns = stat_cols + ["home_team_encoded", "away_team_encoded"]

        # 6. Create input dataframe
        input_df = pd.DataFrame([features], columns=columns)

        # 7. Make prediction
        prediction = model.predict(input_df)[0]

        # 8. Translate result
        if prediction == 'H':
            return "Home Win 🏠"
        elif prediction == 'A':
            return "Away Win 🚗"
        else:
            return "Draw ⚖️"

    except Exception as e:
        logging.error(f"Prediction failed for {home} vs {away}: {e}")
        return "Prediction Error ❌"



def get_teams():
    import pandas as pd
    df = pd.read_csv('E0.csv')  # or your actual data file
    return df['HomeTeam'].unique().tolist()
import requests
from bs4 import BeautifulSoup
import logging

def get_upcoming_fixtures():
    # Manually defined upcoming fixtures - Matchweek 1
    fixtures = [
    {"home": "Liverpool", "away": "Bournemouth", "date": "2025-08-15"},
    {"home": "Aston Villa", "away": "Newcastle", "date": "2025-08-16"},
    {"home": "Brighton", "away": "Fulham", "date": "2025-08-16"},
    {"home": "Sunderland", "away": "West Ham", "date": "2025-08-16"},
    {"home": "Tottenham", "away": "Burnley", "date": "2025-08-16"},
    {"home": "Wolves", "away": "Man City", "date": "2025-08-16"},
    {"home": "Chelsea", "away": "Crystal Palace", "date": "2025-08-17"},
    {"home": "Nottingham Forest", "away": "Brentford", "date": "2025-08-17"},
    {"home": "Manchester United", "away": "Arsenal", "date": "2025-08-17"},
    {"home": "Leeds United", "away": "Everton", "date": "2025-08-18"},
]
    return fixtures

def predict_winner(home, away):
    if home not in le_home.classes_ or away not in le_away.classes_:
        logging.warning(f"Skipping unseen team: {home} or {away}")
    return "Unknown Team ⚠️"

    try:
        # Encode teams
        home_encoded = le_home.transform([home])[0]
        away_encoded = le_away.transform([away])[0]

        # Build feature vector
        home_stats = team_stats.get(home, [0] * stat_cols)
        away_stats = team_stats.get(away, [0] * stat_cols)
        features = home_stats + [home_encoded] + away_stats + [away_encoded]

        # Create input DataFrame
        input_df = pd.DataFrame([features], columns=expected_columns)

        # Predict outcome
        prediction = model.predict(input_df)[0]
        return prediction

    except Exception as e:
        logging.error(f"Prediction failed for {home} vs {away}: {e}")
        return "Prediction Error ❌"


@app.route('/predict', methods=['POST'])
def predict():
    try:
        home_team = request.form['home_team']
        away_team = request.form['away_team']

        # Get recent averages
        home_stats = get_recent_averages(home_team, is_home=True)
        away_stats = get_recent_averages(away_team, is_home=False)

        # Encode teams
        home_encoded = le_home.transform([home_team])[0]
        away_encoded = le_away.transform([away_team])[0]

        # Combine features
        features = home_stats + away_stats + [home_encoded, away_encoded]
        columns = stat_cols + stat_cols + ['home_team_encoded', 'away_team_encoded']
        input_df = pd.DataFrame([features], columns=columns)

        prediction = model.predict(input_df)[0]
        outcome_map = {0: 'Home Win 🏠', 1: 'Draw ⚖️', 2: 'Away Win 🚗'}
        result = outcome_map[prediction]

        return render_template('result.html', prediction=result)

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return f"❌ Error: {e}"



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
