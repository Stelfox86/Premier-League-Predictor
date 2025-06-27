import os # ✅ os module imported for Render deploy
from flask import Flask, render_template, request
import pandas as pd
import joblib
from statistics import mean
predictions = []

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

def get_recent_averages(team, is_home):
    if is_home:
        games = history[history['HomeTeam'] == team].tail(RECENT_MATCHES)
    else:
        games = history[history['AwayTeam'] == team].tail(RECENT_MATCHES)
    return [mean(games[col].fillna(0)) if col in games else 0 for col in stat_cols]
def predict_winner(home, away):
    import random
    return random.choice(["Home Win 🏠", "Draw ⚖️", "Away Win 🚗"])
def get_teams():
    import pandas as pd
    df = pd.read_csv('E0.csv')  # or your actual data file
    return df['HomeTeam'].unique().tolist()
def get_upcoming_fixtures():
    return [
        {"home": "Arsenal", "away": "Chelsea", "date": "2025-08-10"},
        {"home": "Liverpool", "away": "Man City", "date": "2025-08-11"},
        {"home": "Man United", "away": "Tottenham", "date": "2025-08-12"},
    ]



@app.route('/', methods=['GET', 'POST'])
def index():
    predictions = []

    if request.method == 'POST':
        fixtures = get_upcoming_fixtures()  # We'll define this next
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
