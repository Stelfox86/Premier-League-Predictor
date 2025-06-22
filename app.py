import os # ✅ os module imported for Render deploy
from flask import Flask, render_template, request
import pandas as pd
import joblib
from statistics import mean

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

@app.route('/', methods=['GET', 'POST'])
def index():
    import random  # Just in case it's missing
    teams = ['Arsenal', 'Chelsea', 'Liverpool', 'Manchester City']

    if request.method == 'POST':
        home_team = request.form.get('home_team')
        away_team = request.form.get('away_team')

        if home_team and away_team:
            if home_team != away_team:
                try:
                    prediction = random.choice(["Home Win", "Draw", "Away Win"])
                except Exception as e:
                    prediction = f"Prediction error: {str(e)}"
            else:
                prediction = "Please select two different teams."
        else:
            prediction = "Please select both teams."
    else:
        prediction = ""  # Default if no form submitted

    print("→ Template data:", teams, prediction)
    print("✔ Rendering index.html now")
    return render_template('index.html', teams=teams, prediction=prediction, predictions=[])
    # 1. Manual team prediction form
    if 'home_team' in request.form and 'away_team' in request.form:
        home_team = request.form['home_team']
        away_team = request.form['away_team']
        if home_team != away_team:
            try:
                # Swap in your model here if ready
                prediction = random.choice(["Home Win 🏠", "Draw 🤝", "Away Win 🚗"])
            except Exception as e:
                prediction = f"Prediction error: {str(e)}"
        else:
            prediction = "Please select two different teams."

    # 2. Update Predictions button
    else:
        fixtures = [
            {'home': 'Arsenal', 'away': 'Chelsea'},
            {'home': 'Man Utd', 'away': 'Burnley'},
            {'home': 'Brentford', 'away': 'Wolves'}
        ]

        predictions = []
        for match in fixtures:
            outcome = predict_winner(match['home'], match['away'])
            predictions.append({
                'home': match['home'],
                'away': match['away'],
                'outcome': outcome
            })
    return render_template('index.html', teams=teams, prediction=prediction, predictions=predictions)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)