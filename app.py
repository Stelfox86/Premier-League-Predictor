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
import requests
from bs4 import BeautifulSoup
import logging

def get_upcoming_fixtures():
    url = "https://www.bbc.com/sport/football/premier-league/scores-fixtures"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    fixtures = []

    # Each day section
    days = soup.find_all('div', class_='qa-match-block')

    for day in days:
        date_tag = day.find('h3')
        date = date_tag.text.strip() if date_tag else "Upcoming"

        games = day.find_all('li', class_='gs-o-list-ui__item')

        for game in games:
            teams = game.find_all('span', class_='gs-u-display-none gs-u-display-block@m qa-full-team-name')
            if len(teams) == 2:
                home = teams[0].text.strip()
                away = teams[1].text.strip()
                fixtures.append({
                    "home": home,
                    "away": away,
                    "date": date
                })

    logging.info(f"Fixtures found: {len(fixtures)}")
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
