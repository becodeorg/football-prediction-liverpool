"""
Configuration pour l'application Football Prediction
"""

# Configuration du modèle
MODEL_CONFIG = {
    'n_estimators': 100,
    'random_state': 42,
    'features': ['HST', 'HS', 'HC', 'AST', 'AS', 'AC'],
    'target_home': 'FTHG',
    'target_away': 'FTAG'
}

# Configuration Streamlit
STREAMLIT_CONFIG = {
    'page_title': '⚽ Prédiction Futurs Matchs',
    'page_icon': '⚽',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Configuration des données
DATA_CONFIG = {
    'dataset_file': 'dataset.csv',
    'date_column': 'Date',
    'season_column': 'Season'
}
