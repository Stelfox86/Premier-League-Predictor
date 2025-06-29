import logging
import os # ✅ os module imported for Render deploy
from flask import Flask, render_template, request
import pandas as pd
import joblib
from statistics import mean
predictions = []
logging.basicConfig(level=logging.INFO)
API_KEY = os.getenv("API_FOOTBALL_KEY")


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






@app.route('/', methods=['GET', 'POST'])
def index():
    predictions = []

    if request.method == 'POST':
        logging.info("POST request received 🚀 calling fixture API")

        fixtures = get_upcoming_fixtures()
        logging.info(f"Fixtures pulled: {fixtures}")

        for match in fixtures:
            outcome = predict_winner(match['home'], match['away'])
            predictions.append({
                "home": match['home'],
                "away": match['away'],
                "outcome": outcome,
                "date": match['date']
            })

    return render_template('index.html', predictions=predictions)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
