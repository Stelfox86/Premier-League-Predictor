# model/train_model.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def load_data(path='..\\data\\E0.csv'):
    df = pd.read_csv(path)
    return df

def clean_and_prepare(df):
    # Drop unnecessary columns
    cols_to_keep = [
        'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HTHG', 'HTAG',
        'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 
        'HY', 'AY', 'HR', 'AR', 'FTR'
    ]
    df = df[cols_to_keep].dropna()

    # Encode target
    outcome_map = {'H': 0, 'D': 1, 'A': 2}
    df['FTR'] = df['FTR'].map(outcome_map)

    # Encode teams
    le_home = LabelEncoder()
    le_away = LabelEncoder()
    df['HomeTeam'] = le_home.fit_transform(df['HomeTeam'])
    df['AwayTeam'] = le_away.fit_transform(df['AwayTeam'])

    X = df.drop('FTR', axis=1)
    y = df['FTR']
    return X, y, le_home, le_away

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Accuracy: {acc:.2%}")
    print("🔍 Classification report:")
    print(classification_report(y_test, y_pred))

    return clf

def save_model(model, le_home, le_away):
    joblib.dump(model, 'model.pkl')
    joblib.dump(le_home, 'le_home.pkl')
    joblib.dump(le_away, 'le_away.pkl')
    print("✅ All models saved: model.pkl, le_home.pkl, le_away.pkl")


if __name__ == "__main__":
    df = load_data()
    X, y, le_home, le_away = clean_and_prepare(df)
    model = train_model(X, y)
    save_model(model, le_home, le_away)