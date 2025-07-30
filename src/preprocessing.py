"""
Fonctions utilitaires pour le preprocessing des données de football
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ajouter le dossier config au path pour importer la configuration
sys.path.append(str(Path(__file__).parent.parent / "config"))
try:
    from config import *
except ImportError:
    # Valeurs par défaut si config n'est pas trouvé
    FEATURE_COLUMNS = [
        'Div', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 
        'FTHG', 'FTAG', 'FTR', 'HS', 'AS', 'HST', 'AST', 'HC', 'AC'
    ]
    DEFAULT_N_MATCHES = 5

def clean_data(df):
    """
    Nettoie et filtre les données initiales
    
    Args:
        df (pd.DataFrame): Dataset brut
        
    Returns:
        pd.DataFrame: Dataset nettoyé
    """
    # Garder seulement les colonnes spécifiées
    df = df[FEATURE_COLUMNS]
    # Supprimer les lignes avec des valeurs manquantes
    df = df.dropna()
    return df

def get_team_history(df, team, match_date, n_matches, current_idx):
    """
    Récupère l'historique d'une équipe avant une date donnée
    
    Args:
        df (pd.DataFrame): Dataset complet
        team (str): Nom de l'équipe
        match_date: Date du match
        n_matches (int): Nombre de matchs à récupérer
        current_idx (int): Index du match actuel
        
    Returns:
        pd.DataFrame: Historique de l'équipe
    """
    # Matchs où l'équipe joue à domicile ou à l'extérieur, avant la date du match actuel
    team_matches = df[(df.index < current_idx) & 
                     ((df['HomeTeam'] == team) | (df['AwayTeam'] == team))]
    
    # Prendre les N derniers matchs
    team_matches = team_matches.tail(n_matches)
    
    history = []
    for _, match in team_matches.iterrows():
        if match['HomeTeam'] == team:  # Équipe joue à domicile
            goals_scored = match['FTHG']
            goals_conceded = match['FTAG']
            shots = match['HS']
            shots_target = match['HST']
            corners = match['HC']
            result = 'W' if match['FTR'] == 'H' else 'D' if match['FTR'] == 'D' else 'L'
        else:  # Équipe joue à l'extérieur
            goals_scored = match['FTAG']
            goals_conceded = match['FTHG']
            shots = match['AS']
            shots_target = match['AST']
            corners = match['AC']
            result = 'W' if match['FTR'] == 'A' else 'D' if match['FTR'] == 'D' else 'L'
        
        history.append({
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'shots': shots,
            'shots_target': shots_target,
            'corners': corners,
            'result': result
        })
    
    return pd.DataFrame(history)

def calculate_form(history):
    """
    Calcule la forme récente d'une équipe (points sur les derniers matchs)
    
    Args:
        history (pd.DataFrame): Historique des matchs
        
    Returns:
        float: Forme moyenne (points par match)
    """
    if len(history) == 0:
        return 0
    
    points = []
    for _, match in history.iterrows():
        if match['result'] == 'W':
            points.append(3)
        elif match['result'] == 'D':
            points.append(1)
        else:
            points.append(0)
    
    return sum(points) / len(points)  # Moyenne de points par match

def create_team_features(df, n_matches=DEFAULT_N_MATCHES):
    """
    Crée des features basées sur l'historique des équipes
    
    Args:
        df (pd.DataFrame): Dataset nettoyé
        n_matches (int): Nombre de matchs d'historique à considérer
        
    Returns:
        pd.DataFrame: Dataset avec features d'historique
    """
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
    df = df.sort_values(['Date', 'Time'])
    
    features_list = []
    
    for idx, row in df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        match_date = row['Date']
        
        # Récupérer les N derniers matchs pour chaque équipe AVANT ce match
        home_history = get_team_history(df, home_team, match_date, n_matches, idx)
        away_history = get_team_history(df, away_team, match_date, n_matches, idx)
        
        # Créer les features
        match_features = {
            'Date': match_date,
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            'Target': row['FTR'],  # H, D, A
            
            # Features équipe domicile
            'home_avg_goals_scored': home_history['goals_scored'].mean() if len(home_history) > 0 else 0,
            'home_avg_goals_conceded': home_history['goals_conceded'].mean() if len(home_history) > 0 else 0,
            'home_avg_shots': home_history['shots'].mean() if len(home_history) > 0 else 0,
            'home_avg_shots_target': home_history['shots_target'].mean() if len(home_history) > 0 else 0,
            'home_avg_corners': home_history['corners'].mean() if len(home_history) > 0 else 0,
            'home_win_rate': (home_history['result'] == 'W').mean() if len(home_history) > 0 else 0,
            'home_form': calculate_form(home_history),
            
            # Features équipe extérieur
            'away_avg_goals_scored': away_history['goals_scored'].mean() if len(away_history) > 0 else 0,
            'away_avg_goals_conceded': away_history['goals_conceded'].mean() if len(away_history) > 0 else 0,
            'away_avg_shots': away_history['shots'].mean() if len(away_history) > 0 else 0,
            'away_avg_shots_target': away_history['shots_target'].mean() if len(away_history) > 0 else 0,
            'away_avg_corners': away_history['corners'].mean() if len(away_history) > 0 else 0,
            'away_win_rate': (away_history['result'] == 'W').mean() if len(away_history) > 0 else 0,
            'away_form': calculate_form(away_history),
        }
        
        features_list.append(match_features)
    
    return pd.DataFrame(features_list)

def add_additional_features(df):
    """
    Ajoute des features supplémentaires dérivées
    
    Args:
        df (pd.DataFrame): Dataset avec features de base
        
    Returns:
        pd.DataFrame: Dataset avec features additionnelles
    """
    # Différence de forme entre les équipes
    df['form_difference'] = df['home_form'] - df['away_form']
    
    # Différence de buts marqués/encaissés
    df['goal_difference'] = (df['home_avg_goals_scored'] - df['home_avg_goals_conceded']) - \
                           (df['away_avg_goals_scored'] - df['away_avg_goals_conceded'])
    
    # Efficacité des tirs
    df['home_shot_efficiency'] = df['home_avg_shots_target'] / (df['home_avg_shots'] + 1)  # +1 pour éviter division par 0
    df['away_shot_efficiency'] = df['away_avg_shots_target'] / (df['away_avg_shots'] + 1)
    
    # Avantage du terrain
    df['home_advantage'] = df['home_win_rate'] - df['away_win_rate']
    
    return df

def validate_and_clean_features(df):
    """
    Valide et nettoie le dataset final
    
    Args:
        df (pd.DataFrame): Dataset avec toutes les features
        
    Returns:
        pd.DataFrame: Dataset final nettoyé
    """
    # Supprimer les matchs sans historique suffisant
    df = df.dropna()
    
    # Encoder la variable cible
    target_mapping = {'H': 0, 'D': 1, 'A': 2}  # Home, Draw, Away
    df['Target_encoded'] = df['Target'].map(target_mapping)
    
    # Supprimer les outliers extrêmes si nécessaire
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col != 'Target_encoded':
            Q1 = df[col].quantile(0.01)
            Q3 = df[col].quantile(0.99)
            df = df[(df[col] >= Q1) & (df[col] <= Q3)]
    
    return df
