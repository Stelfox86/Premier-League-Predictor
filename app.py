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

def predict_winner(home, away):
    try:
        # Skip if the team is not recognized by the model
        if home not in le_home.classes_ or away not in le_away.classes_:
            return "Prediction Error ❌ (Unknown team)"

        # Get recent average stats
        home_avg = get_recent_averages(home, is_home=True)
        away_avg = get_recent_averages(away, is_home=False)

        # Combine averages into one input row
        features = home_avg + away_avg

        # Encode team names
        home_encoded = le_home.transform([home])[0]
        away_encoded = le_away.transform([away])[0]

        # Add encoded team names to features
        features += [home_encoded, away_encoded]
        

        # Match the column order expected by the model
        columns = stat_cols + ["home_team_encoded", "away_team_encoded"]

        input_df = pd.DataFrame([features], columns=columns)

        # Make prediction
        prediction = model.predict(input_df)[0]

        # Translate prediction
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
    {"home": "Nott'm Forest", "away": "Brentford", "date": "2025-08-17"},
    {"home": "Man United", "away": "Arsenal", "date": "2025-08-17"},
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
