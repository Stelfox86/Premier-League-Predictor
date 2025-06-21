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

@app.route('/', methods=['GET', 'POST'])
def index():
    teams = sorted(set(history['HomeTeam']).union(set(history['AwayTeam'])))
    prediction = ""
    if request.method == 'POST':
        home = request.form['home']
        away = request.form['away']
        if home != away:
            try:
                h_enc = le_home.transform([home])[0]
                a_enc = le_away.transform([away])[0]
                h_stats = get_recent_averages(home, True)
                a_stats = get_recent_averages(away, False)
                blended = [(h + a) / 2 for h, a in zip(h_stats, a_stats)]
                input_row = pd.DataFrame([[h_enc, a_enc] + blended],
                                         columns=['HomeTeam', 'AwayTeam'] + stat_cols)
                pred = model.predict(input_row)[0]
                result_map = {0: "Home Win 🏠", 1: "Draw 🤝", 2: "Away Win 🚗"}
                prediction = result_map[pred]
            except Exception as e:
                prediction = f"Error: {e}"
    return render_template('index.html', teams=teams, prediction=prediction)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)