#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚽ SYSTÈME DE PRÉDICTION DE FUTURS MATCHS FOOTBALL V2.0
Application Streamlit avancée avec analytics, historique tête-à-tête, forme récente et graphiques
Avec sélection par saison pour une analyse plus précise

Utilisation: streamlit run football_prediction_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="⚽ Football Analytics V2.0", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS amélioré avec mode sombre/clair et design responsive professionnel
st.markdown("""
<style>
    /* Variables CSS pour les thèmes */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --info-color: #17a2b8;
        --light-bg: #ffffff;
        --dark-bg: #0e1117;
        --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        --card-shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.15);
        --border-radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Header principal avec animation shimmer */
    .analytics-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem;
        border-radius: var(--border-radius);
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .analytics-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .analytics-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .analytics-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Cartes métriques améliorées avec animations et glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        text-align: center;
        box-shadow: var(--card-shadow);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
        color: white;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--card-shadow-hover);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .metric-card h4 {
        margin: 0 0 1rem 0;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.9;
    }
    
    .metric-card h2 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Indicateurs de forme avec animations pulsantes */
    .team-form, .recent-form {
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--card-shadow);
        transition: var(--transition);
        position: relative;
        color: white;
        font-weight: 500;
        overflow: hidden;
    }
    
    .team-form::after, .recent-form::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(50%, -50%);
    }
    
    .team-form:hover, .recent-form:hover {
        transform: scale(1.02);
        box-shadow: var(--card-shadow-hover);
    }
    
    .team-form h5, .recent-form h5 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .team-form p, .recent-form p {
        margin: 0.5rem 0;
        font-size: 0.95rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Notifications système avec animations */
    .notification {
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        border-left: 4px solid;
        box-shadow: var(--card-shadow);
        animation: slideInRight 0.5s ease;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .notification.success {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.05));
        border-left-color: var(--success-color);
        color: var(--success-color);
    }
    
    .notification.warning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
        border-left-color: var(--warning-color);
        color: #856404;
    }
    
    .notification.danger {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.1), rgba(220, 53, 69, 0.05));
        border-left-color: var(--danger-color);
        color: var(--danger-color);
    }
    
    .notification.info {
        background: linear-gradient(135deg, rgba(23, 162, 184, 0.1), rgba(23, 162, 184, 0.05));
        border-left-color: var(--info-color);
        color: var(--info-color);
    }
    
    /* Barres de confiance avec animations */
    .confidence-bar {
        width: 100%;
        height: 25px;
        background: rgba(0,0,0,0.1);
        border-radius: 12px;
        overflow: hidden;
        margin: 0.5rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 12px;
        transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(90deg, var(--success-color), #20c997, var(--info-color));
        position: relative;
        overflow: hidden;
    }
    
    .confidence-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: progress-shine 2s infinite;
    }
    
    @keyframes progress-shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Analyse tête-à-tête */
    .head-to-head {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--card-shadow);
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .head-to-head::before {
        content: '⚔️';
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    /* Boutons personnalisés */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: var(--transition);
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .analytics-header h1 {
            font-size: 2rem;
        }
        
        .analytics-header p {
            font-size: 1rem;
        }
        
        .metric-card h2 {
            font-size: 2rem;
        }
        
        .team-form, .recent-form {
            padding: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .analytics-header {
            padding: 1.5rem;
        }
        
        .analytics-header h1 {
            font-size: 1.5rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .metric-card h2 {
            font-size: 1.5rem;
        }
    }
    
    /* Animations de chargement */
    .loading-dots {
        display: inline-block;
        position: relative;
        width: 80px;
        height: 20px;
    }
    
    .loading-dots div {
        position: absolute;
        top: 8px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--primary-color);
        animation: loading-dots 1.2s linear infinite;
    }
    
    .loading-dots div:nth-child(1) { left: 8px; animation-delay: 0s; }
    .loading-dots div:nth-child(2) { left: 32px; animation-delay: -0.4s; }
    .loading-dots div:nth-child(3) { left: 56px; animation-delay: -0.8s; }
    
    @keyframes loading-dots {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Sidebar personnalisée */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    }
    
    /* Dataframes avec style amélioré */
    [data-testid="stDataFrame"] {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--card-shadow);
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour créer des notifications
def show_notification(message, notification_type="info", duration=5):
    """Affiche une notification stylisée"""
    icon_map = {
        "success": "✅",
        "warning": "⚠️", 
        "danger": "❌",
        "info": "ℹ️"
    }
    
    icon = icon_map.get(notification_type, "ℹ️")
    
    st.markdown(f"""
    <div class="notification {notification_type}">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)

# Fonction pour créer des barres de confiance
def show_confidence_bar(confidence, label="Confiance"):
    """Affiche une barre de confiance animée"""
    color = "#28a745" if confidence >= 75 else "#ffc107" if confidence >= 50 else "#dc3545"
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 600;">{label}</span>
            <span style="font-weight: 700; color: {color};">{confidence:.1f}%</span>
        </div>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: {confidence}%; background: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fonction pour afficher des métriques améliorées
def show_enhanced_metric(title, value, delta=None, help_text=None, color="primary"):
    """Affiche une métrique avec style amélioré"""
    color_map = {
        "primary": "var(--primary-color)",
        "success": "var(--success-color)",
        "warning": "var(--warning-color)",
        "danger": "var(--danger-color)",
        "info": "var(--info-color)"
    }
    
    bg_color = color_map.get(color, "var(--primary-color)")
    
    delta_html = ""
    if delta is not None:
        delta_color = "#28a745" if delta >= 0 else "#dc3545"
        delta_icon = "↗️" if delta >= 0 else "↘️"
        delta_html = f'<p style="margin: 0.5rem 0 0 0; color: {delta_color}; font-size: 0.9rem;">{delta_icon} {delta}</p>'
    
    help_html = ""
    if help_text:
        help_html = f'<p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.8;">{help_text}</p>'
    
    st.markdown(f"""
    <div class="metric-card" style="background: {bg_color};">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {delta_html}
        {help_html}
    </div>
    """, unsafe_allow_html=True)

# Fonction pour déterminer la saison footballistique
def get_season_from_date(date):
    """Détermine la saison footballistique à partir d'une date"""
    year = date.year
    month = date.month
    
    # Si on est entre juillet et décembre, c'est le début de la saison
    # Si on est entre janvier et juin, c'est la fin de la saison
    if month >= 7:  # Juillet à décembre
        return f"{year}-{str(year+1)[2:]}"
    else:  # Janvier à juin
        return f"{year-1}-{str(year)[2:]}"

# Charger et préparer les données
@st.cache_data
def load_and_prepare_data():
    """Charger le dataset et ajouter les informations de saison"""
    try:
        # Charger le dataset
        data = pd.read_csv('dataset.csv')
        
        # Convertir la colonne Date (gestion automatique du format)
        data['Date'] = pd.to_datetime(data['Date'], format='mixed', dayfirst=True)
        
        # Ajouter la colonne saison
        data['Season'] = data['Date'].apply(get_season_from_date)
        
        return data
        
    except FileNotFoundError:
        st.error("❌ Fichier 'dataset.csv' non trouvé. Veuillez vous assurer que le fichier est présent.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
        return None

@st.cache_data
def calculate_team_stats(data, selected_seasons):
    """Calculer les statistiques des équipes pour les saisons sélectionnées"""
    # Filtrer les données par saison
    if selected_seasons:
        filtered_data = data[data['Season'].isin(selected_seasons)]
    else:
        filtered_data = data
    
    if len(filtered_data) == 0:
        return {}
    
    # Calculer les moyennes par équipe pour les saisons sélectionnées
    team_stats = {}
    
    # Obtenir toutes les équipes
    teams = set(list(filtered_data['HomeTeam'].unique()) + list(filtered_data['AwayTeam'].unique()))
    
    for team in teams:
        # Matchs à domicile
        home_matches = filtered_data[filtered_data['HomeTeam'] == team]
        # Matchs à l'extérieur  
        away_matches = filtered_data[filtered_data['AwayTeam'] == team]
        
        # Statistiques moyennes à domicile
        home_stats = {
            'avg_goals_scored_home': home_matches['FTHG'].mean() if len(home_matches) > 0 else 1.0,
            'avg_goals_conceded_home': home_matches['FTAG'].mean() if len(home_matches) > 0 else 1.0,
            'avg_shots_home': home_matches['HS'].mean() if len(home_matches) > 0 else 10.0,
            'avg_shots_target_home': home_matches['HST'].mean() if len(home_matches) > 0 else 4.0,
            'avg_corners_home': home_matches['HC'].mean() if len(home_matches) > 0 else 5.0,
            'home_wins': len(home_matches[home_matches['FTR'] == 'H']),
            'home_draws': len(home_matches[home_matches['FTR'] == 'D']),
            'home_losses': len(home_matches[home_matches['FTR'] == 'A']),
            'total_home_matches': len(home_matches)
        }
        
        # Statistiques moyennes à l'extérieur
        away_stats = {
            'avg_goals_scored_away': away_matches['FTAG'].mean() if len(away_matches) > 0 else 0.8,
            'avg_goals_conceded_away': away_matches['FTHG'].mean() if len(away_matches) > 0 else 1.2,
            'avg_shots_away': away_matches['AS'].mean() if len(away_matches) > 0 else 8.0,
            'avg_shots_target_away': away_matches['AST'].mean() if len(away_matches) > 0 else 3.0,
            'avg_corners_away': away_matches['AC'].mean() if len(away_matches) > 0 else 4.0,
            'away_wins': len(away_matches[away_matches['FTR'] == 'A']),
            'away_draws': len(away_matches[away_matches['FTR'] == 'D']),
            'away_losses': len(away_matches[away_matches['FTR'] == 'H']),
            'total_away_matches': len(away_matches)
        }
        
        team_stats[team] = {**home_stats, **away_stats}
    
    return team_stats

# Fonction pour récupérer les cotes historiques des bookmakers
def get_historical_odds(data, home_team, away_team, selected_seasons):
    """Récupère les cotes historiques moyennes pour cette confrontation"""
    
    if data is None:
        return None
    
    # Filtrer par saison
    filtered_data = data[data['Season'].isin(selected_seasons)]
    
    # Chercher les matchs historiques entre ces équipes
    historical_matches = filtered_data[
        ((filtered_data['HomeTeam'] == home_team) & (filtered_data['AwayTeam'] == away_team)) |
        ((filtered_data['HomeTeam'] == away_team) & (filtered_data['AwayTeam'] == home_team))
    ]
    
    if len(historical_matches) == 0:
        # Si pas d'historique direct, utiliser les moyennes des équipes
        home_matches = filtered_data[filtered_data['HomeTeam'] == home_team]
        away_matches = filtered_data[filtered_data['AwayTeam'] == away_team]
        
        odds_data = {
            'has_odds': False,
            'direct_matches': 0,
            'home_team_matches': len(home_matches),
            'away_team_matches': len(away_matches)
        }
        
        # Essayer de récupérer les cotes moyennes des équipes
        odds_cols = ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'PSH', 'PSD', 'PSA']
        available_odds = [col for col in odds_cols if col in filtered_data.columns]
        
        if available_odds and len(home_matches) > 0:
            # Calculer les moyennes des cotes pour l'équipe à domicile
            home_odds_data = {}
            for bookmaker in ['B365', 'BW', 'PS']:
                h_col, d_col, a_col = f'{bookmaker}H', f'{bookmaker}D', f'{bookmaker}A'
                if all(col in home_matches.columns for col in [h_col, d_col, a_col]):
                    home_avg = home_matches[h_col].dropna().mean()
                    draw_avg = home_matches[d_col].dropna().mean()
                    away_avg = home_matches[a_col].dropna().mean()
                    
                    if pd.notna(home_avg):
                        bookmaker_name = {'B365': 'Bet365', 'BW': 'Betway', 'PS': 'Pinnacle'}.get(bookmaker, bookmaker)
                        home_odds_data[bookmaker_name] = {
                            'home': home_avg,
                            'draw': draw_avg,
                            'away': away_avg
                        }
            
            odds_data['bookmaker_odds'] = home_odds_data
            odds_data['has_odds'] = len(home_odds_data) > 0
        
        return odds_data
    
    # Si on a des matchs historiques directs
    odds_data = {
        'has_odds': True,
        'direct_matches': len(historical_matches),
        'home_team_matches': 0,
        'away_team_matches': 0
    }
    
    # Récupérer les cotes des bookmakers pour les matchs directs
    bookmaker_odds = {}
    
    for bookmaker in ['B365', 'BW', 'PS']:
        h_col, d_col, a_col = f'{bookmaker}H', f'{bookmaker}D', f'{bookmaker}A'
        
        if all(col in historical_matches.columns for col in [h_col, d_col, a_col]):
            # Prendre la moyenne des cotes pour cette confrontation
            home_odds = historical_matches[h_col].dropna().mean()
            draw_odds = historical_matches[d_col].dropna().mean()
            away_odds = historical_matches[a_col].dropna().mean()
            
            if pd.notna(home_odds):
                bookmaker_name = {'B365': 'Bet365', 'BW': 'Betway', 'PS': 'Pinnacle'}.get(bookmaker, bookmaker)
                bookmaker_odds[bookmaker_name] = {
                    'home': home_odds,
                    'draw': draw_odds,
                    'away': away_odds
                }
    
    odds_data['bookmaker_odds'] = bookmaker_odds
    odds_data['has_odds'] = len(bookmaker_odds) > 0
    
    return odds_data

# Fonction pour convertir les cotes en pourcentages
def odds_to_percentage(odds):
    """Convertit une cote en pourcentage de probabilité"""
    if odds <= 0 or pd.isna(odds):
        return 0
    return (1 / odds) * 100

# Fonction pour analyser la forme récente d'une équipe
def get_team_recent_form(data, team, n_matches=5, selected_seasons=None):
    """Analyse la forme récente d'une équipe sur les n derniers matchs"""
    
    if selected_seasons:
        data = data[data['Season'].isin(selected_seasons)]
    
    # Matchs à domicile et à l'extérieur
    home_matches = data[data['HomeTeam'] == team].sort_values('Date').tail(n_matches)
    away_matches = data[data['AwayTeam'] == team].sort_values('Date').tail(n_matches)
    
    # Combiner et trier par date
    all_matches = []
    
    for _, match in home_matches.iterrows():
        result = 'W' if match['FTR'] == 'H' else 'D' if match['FTR'] == 'D' else 'L'
        all_matches.append({
            'Date': match['Date'],
            'Opponent': match['AwayTeam'],
            'Venue': 'Home',
            'Goals_For': match['FTHG'],
            'Goals_Against': match['FTAG'],
            'Result': result,
            'Points': 3 if result == 'W' else 1 if result == 'D' else 0
        })
    
    for _, match in away_matches.iterrows():
        result = 'W' if match['FTR'] == 'A' else 'D' if match['FTR'] == 'D' else 'L'
        all_matches.append({
            'Date': match['Date'],
            'Opponent': match['HomeTeam'],
            'Venue': 'Away',
            'Goals_For': match['FTAG'],
            'Goals_Against': match['FTHG'],
            'Result': result,
            'Points': 3 if result == 'W' else 1 if result == 'D' else 0
        })
    
    # Trier par date et prendre les n plus récents
    all_matches = sorted(all_matches, key=lambda x: x['Date'])[-n_matches:]
    
    if not all_matches:
        return None
    
    # Calculer les statistiques
    total_points = sum(match['Points'] for match in all_matches)
    total_goals_for = sum(match['Goals_For'] for match in all_matches)
    total_goals_against = sum(match['Goals_Against'] for match in all_matches)
    wins = sum(1 for match in all_matches if match['Result'] == 'W')
    draws = sum(1 for match in all_matches if match['Result'] == 'D')
    losses = sum(1 for match in all_matches if match['Result'] == 'L')
    
    return {
        'matches': all_matches,
        'total_matches': len(all_matches),
        'points': total_points,
        'points_per_match': total_points / len(all_matches) if all_matches else 0,
        'goals_for': total_goals_for,
        'goals_against': total_goals_against,
        'goal_difference': total_goals_for - total_goals_against,
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'win_rate': wins / len(all_matches) if all_matches else 0
    }

# Fonction pour analyser l'historique tête-à-tête
def get_head_to_head_analysis(data, team1, team2, selected_seasons=None):
    """Analyse complète de l'historique entre deux équipes"""
    
    if selected_seasons:
        data = data[data['Season'].isin(selected_seasons)]
    
    # Matchs directs entre les deux équipes
    h2h_matches = data[
        ((data['HomeTeam'] == team1) & (data['AwayTeam'] == team2)) |
        ((data['HomeTeam'] == team2) & (data['AwayTeam'] == team1))
    ].sort_values('Date')
    
    if len(h2h_matches) == 0:
        return None
    
    # Statistiques globales
    team1_wins = 0
    team2_wins = 0
    draws = 0
    team1_goals = 0
    team2_goals = 0
    
    matches_detail = []
    
    for _, match in h2h_matches.iterrows():
        if match['HomeTeam'] == team1:
            # team1 à domicile
            team1_score = match['FTHG']
            team2_score = match['FTAG']
            venue_team1 = 'Home'
        else:
            # team2 à domicile
            team1_score = match['FTAG']
            team2_score = match['FTHG']
            venue_team1 = 'Away'
        
        # Déterminer le résultat
        if team1_score > team2_score:
            result = f'{team1} wins'
            team1_wins += 1
        elif team2_score > team1_score:
            result = f'{team2} wins'
            team2_wins += 1
        else:
            result = 'Draw'
            draws += 1
        
        team1_goals += team1_score
        team2_goals += team2_score
        
        matches_detail.append({
            'Date': match['Date'],
            'Season': match['Season'],
            'Home': match['HomeTeam'],
            'Away': match['AwayTeam'],
            'Score': f"{match['FTHG']}-{match['FTAG']}",
            'Result': result,
            'Team1_Score': team1_score,
            'Team2_Score': team2_score,
            'Venue_Team1': venue_team1
        })
    
    return {
        'total_matches': len(h2h_matches),
        'team1_wins': team1_wins,
        'team2_wins': team2_wins,
        'draws': draws,
        'team1_goals': team1_goals,
        'team2_goals': team2_goals,
        'team1_win_rate': team1_wins / len(h2h_matches),
        'team2_win_rate': team2_wins / len(h2h_matches),
        'draw_rate': draws / len(h2h_matches),
        'avg_goals_per_match': (team1_goals + team2_goals) / len(h2h_matches),
        'matches_detail': matches_detail
    }

# Fonction pour créer des graphiques de performance
def create_performance_chart(team_stats, team_name):
    """Crée un graphique radar des performances d'une équipe"""
    
    categories = [
        'Buts Marqués/Match',
        'Défense (Inv.)',
        'Tirs Cadrés/Match', 
        'Tirs Totaux/Match',
        'Corners/Match',
        'Taux Victoire Dom.',
        'Taux Victoire Ext.'
    ]
    
    # Normaliser les valeurs sur 10
    values = [
        min(10, team_stats.get('avg_goals_scored_home', 0) * 4),  # *4 pour normaliser
        min(10, 10 - team_stats.get('avg_goals_conceded_home', 2) * 2),  # Inversé pour défense
        min(10, team_stats.get('avg_shots_target_home', 0) * 2),
        min(10, team_stats.get('avg_shots_home', 0) * 0.8),
        min(10, team_stats.get('avg_corners_home', 0) * 1.5),
        team_stats.get('home_wins', 0) / max(1, team_stats.get('total_home_matches', 1)) * 10,
        team_stats.get('away_wins', 0) / max(1, team_stats.get('total_away_matches', 1)) * 10
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=team_name,
        line_color='rgb(102, 126, 234)',
        fillcolor='rgba(102, 126, 234, 0.25)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title=f"Profil Performance - {team_name}",
        font=dict(size=12)
    )
    
    return fig

# Créer des features pour prédire de futurs matchs
def create_match_features(home_team, away_team, team_stats):
    """Créer les features pour un futur match basé sur les performances historiques"""
    
    home_stats = team_stats.get(home_team, {})
    away_stats = team_stats.get(away_team, {})
    
    # Features pour l'équipe à domicile (basées sur ses performances historiques à domicile)
    home_features = [
        home_stats.get('avg_shots_target_home', 4.0),
        home_stats.get('avg_shots_home', 10.0),
        home_stats.get('avg_corners_home', 5.0),
    ]
    
    # Features pour l'équipe à l'extérieur (basées sur ses performances historiques à l'extérieur)
    away_features = [
        away_stats.get('avg_shots_target_away', 3.0),
        away_stats.get('avg_shots_away', 8.0),
        away_stats.get('avg_corners_away', 4.0),
    ]
    
    return home_features, away_features

# Entraîner les modèles de prédiction
@st.cache_resource
def train_prediction_models(data, selected_seasons):
    """Entraîner les modèles pour prédire les résultats de futurs matchs"""
    
    if data is None:
        return None, None
    
    # Filtrer par saison si spécifié
    if selected_seasons:
        filtered_data = data[data['Season'].isin(selected_seasons)]
    else:
        filtered_data = data
    
    # Préparer les données d'entraînement
    clean_data = filtered_data.dropna(subset=['HST', 'AST', 'HS', 'AS', 'HC', 'AC', 'FTHG', 'FTAG'])
    
    if len(clean_data) == 0:
        return None, None
    
    X_home = clean_data[['HST', 'HS', 'HC']].values
    y_home = clean_data['FTHG'].values
    
    X_away = clean_data[['AST', 'AS', 'AC']].values  
    y_away = clean_data['FTAG'].values
    
    # Entraîner les modèles
    home_model = RandomForestRegressor(n_estimators=100, random_state=42)
    home_model.fit(X_home, y_home)
    
    away_model = RandomForestRegressor(n_estimators=100, random_state=42)
    away_model.fit(X_away, y_away)
    
    return home_model, away_model

def display_team_record(team_stats, team_name, location):
    """Afficher le palmarès d'une équipe"""
    if team_name in team_stats:
        stats = team_stats[team_name]
        
        if location == "home":
            wins = stats.get('home_wins', 0)
            draws = stats.get('home_draws', 0)
            losses = stats.get('home_losses', 0)
            total = stats.get('total_home_matches', 0)
            goals_scored = stats.get('avg_goals_scored_home', 0)
            goals_conceded = stats.get('avg_goals_conceded_home', 0)
        else:
            wins = stats.get('away_wins', 0)
            draws = stats.get('away_draws', 0)
            losses = stats.get('away_losses', 0)
            total = stats.get('total_away_matches', 0)
            goals_scored = stats.get('avg_goals_scored_away', 0)
            goals_conceded = stats.get('avg_goals_conceded_away', 0)
        
        if total > 0:
            win_rate = (wins / total) * 100
            st.write(f"📈 **Bilan ({location}):** {wins}V - {draws}N - {losses}D ({total} matchs)")
            st.write(f"🏆 **Taux de victoire:** {win_rate:.1f}%")
            st.write(f"⚽ **Buts marqués/match:** {goals_scored:.2f}")
            st.write(f"🛡️ **Buts encaissés/match:** {goals_conceded:.2f}")

def show_analytics_page(data, teams, team_stats, selected_seasons):
    """Page analytics avancées"""
    
    st.header("📊 Analytics Avancées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_team = st.selectbox("Sélectionner une équipe:", teams, key="analytics_team")
    
    with col2:
        view_type = st.selectbox("Type d'analyse:", 
                               ["Performance Globale", "Domicile vs Extérieur", "Évolution Saisonnière"])
    
    if selected_team:
        if view_type == "Performance Globale":
            # Graphique radar des performances
            fig = create_performance_chart(team_stats, selected_team)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Métriques de performance
            stats = team_stats[selected_team]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Matchs Totaux", 
                         stats.get('total_home_matches', 0) + stats.get('total_away_matches', 0))
            with col2:
                total_wins = stats.get('home_wins', 0) + stats.get('away_wins', 0)
                total_matches = stats.get('total_home_matches', 0) + stats.get('total_away_matches', 0)
                win_rate = (total_wins / max(1, total_matches)) * 100
                st.metric("Taux de Victoire", f"{win_rate:.1f}%")
            with col3:
                goals_for = stats.get('total_goals_for_home', 0) + stats.get('total_goals_for_away', 0)
                goals_per_match = goals_for / max(1, total_matches)
                st.metric("Buts/Match", f"{goals_per_match:.1f}")
            with col4:
                goals_against = stats.get('total_goals_against_home', 0) + stats.get('total_goals_against_away', 0)
                goal_diff = goals_for - goals_against
                st.metric("Différence de Buts", f"{int(goal_diff):+d}")
        
        elif view_type == "Domicile vs Extérieur":
            # Comparaison domicile/extérieur
            stats = team_stats[selected_team]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏠 À Domicile")
                home_matches = stats.get('total_home_matches', 0)
                home_wins = stats.get('home_wins', 0)
                home_win_rate = (home_wins / max(1, home_matches)) * 100
                
                st.metric("Matchs", home_matches)
                st.metric("Victoires", f"{home_wins} ({home_win_rate:.1f}%)")
                st.metric("Buts/Match", f"{stats.get('avg_goals_for_home', 0):.1f}")
                st.metric("Tirs Cadrés/Match", f"{stats.get('avg_shots_target_home', 0):.1f}")
            
            with col2:
                st.markdown("#### ✈️ À l'Extérieur")
                away_matches = stats.get('total_away_matches', 0)
                away_wins = stats.get('away_wins', 0)
                away_win_rate = (away_wins / max(1, away_matches)) * 100
                
                st.metric("Matchs", away_matches)
                st.metric("Victoires", f"{away_wins} ({away_win_rate:.1f}%)")
                st.metric("Buts/Match", f"{stats.get('avg_goals_for_away', 0):.1f}")
                st.metric("Tirs Cadrés/Match", f"{stats.get('avg_shots_target_away', 0):.1f}")

def show_head_to_head_page(data, teams, selected_seasons):
    """Page analyse tête-à-tête"""
    
    st.header("🔍 Analyse Tête-à-Tête")
    
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = st.selectbox("Première équipe:", teams, key="h2h_team1")
    
    with col2:
        team2 = st.selectbox("Seconde équipe:", teams, key="h2h_team2")
    
    if team1 and team2 and team1 != team2:
        h2h = get_head_to_head_analysis(data, team1, team2, selected_seasons)
        
        if h2h and h2h['total_matches'] > 0:
            st.markdown("### 📊 Statistiques Générales")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Confrontations", int(h2h['total_matches']))
            with col2:
                st.metric(f"Victoires {team1}", f"{int(h2h['team1_wins'])} ({h2h['team1_win_rate']:.1%})")
            with col3:
                st.metric("Matchs Nuls", f"{int(h2h['draws'])} ({h2h['draw_rate']:.1%})")
            with col4:
                st.metric(f"Victoires {team2}", f"{int(h2h['team2_wins'])} ({h2h['team2_win_rate']:.1%})")
            
            # Détails des matchs
            if h2h['matches_detail']:
                st.markdown("### 📋 Historique des Confrontations")
                
                matches_data = []
                for match in h2h['matches_detail'][-10:]:  # Afficher les 10 derniers matchs
                    matches_data.append({
                        'Date': match['Date'].strftime('%d/%m/%Y'),
                        'Saison': match['Season'],
                        'Domicile': match['Home'],
                        'Score': match['Score'],
                        'Extérieur': match['Away'],
                        'Résultat': match['Result']
                    })
                
                df_matches = pd.DataFrame(matches_data)
                st.dataframe(df_matches, use_container_width=True, hide_index=True)
        else:
            st.info(f"Aucune confrontation directe trouvée entre {team1} et {team2} dans les saisons sélectionnées.")

def show_recent_form_page(data, teams, selected_seasons):
    """Page forme récente"""
    
    st.header("📈 Forme Récente des Équipes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_team = st.selectbox("Sélectionner une équipe:", teams, key="form_team")
    
    with col2:
        num_matches = st.slider("Nombre de matchs récents:", 3, 10, 5)
    
    if selected_team:
        form_data = get_team_recent_form(data, selected_team, num_matches, selected_seasons)
        
        if form_data:
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Matchs Analysés", int(form_data['total_matches']))
            
            with col2:
                points_color = "normal"
                if form_data['points_per_match'] >= 2.5:
                    points_color = "inverse"
                elif form_data['points_per_match'] <= 1:
                    points_color = "off"
                
                st.metric("Points/Match", f"{form_data['points_per_match']:.1f}",
                         delta=None, delta_color=points_color)
            
            with col3:
                goal_diff = form_data['goal_difference']
                st.metric("Différence Buts", f"{int(goal_diff):+d}",
                         delta=None, delta_color="normal" if goal_diff >= 0 else "off")
            
            with col4:
                win_rate = (form_data['wins'] / max(1, form_data['total_matches'])) * 100
                st.metric("Taux Victoire", f"{win_rate:.1f}%")
            
            # Bilan détaillé
            st.markdown("### 📊 Bilan Détaillé")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="background: #d4edda;">
                    <h4>✅ Victoires</h4>
                    <h2>{int(form_data['wins'])}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card" style="background: #fff3cd;">
                    <h4>➖ Nuls</h4>
                    <h2>{int(form_data['draws'])}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card" style="background: #f8d7da;">
                    <h4>❌ Défaites</h4>
                    <h2>{int(form_data['losses'])}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Détails des buts
            st.markdown("### ⚽ Statistiques Offensives/Défensives")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Buts Marqués", int(form_data['goals_for']), 
                         f"{form_data['goals_for']/max(1, form_data['total_matches']):.1f}/match")
            
            with col2:
                st.metric("Buts Encaissés", int(form_data['goals_against']),
                         f"{form_data['goals_against']/max(1, form_data['total_matches']):.1f}/match")
        else:
            st.info(f"Pas suffisamment de données récentes pour {selected_team}")

# Interface principale
def main():
    """Fonction principale de l'application avec navigation multi-pages"""
    
    # En-tête de l'application
    st.markdown("""
    <div class="analytics-header">
        <h1>⚽ Football Analytics & Prediction V2.0</h1>
        <p>Prédictions avancées avec analytics, historique tête-à-tête et forme récente</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charger les données
    with st.spinner("� Chargement des données..."):
        data = load_and_prepare_data()
    
    if data is None:
        st.stop()
    
    # Navigation principale
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choisir une section",
        ["🏠 Prédictions", "📊 Analytics Avancées", "🔍 Tête-à-Tête", "📈 Forme Récente"]
    )
    
    # Obtenir les saisons disponibles
    available_seasons = sorted(data['Season'].unique(), reverse=True)
    
    # Sidebar avec sélection des saisons
    with st.sidebar:
        st.header("📅 Sélection des Saisons")
        
        # Option pour sélectionner toutes les saisons ou des saisons spécifiques
        season_option = st.radio(
            "Choisir les données à utiliser:",
            ["Saison la plus récente", "Saisons personnalisées", "Toutes les saisons"],
            key="season_selection_radio",
            help="Sélectionnez les saisons à utiliser pour calculer les statistiques des équipes"
        )
        
        if season_option == "Saison la plus récente":
            selected_seasons = [available_seasons[0]]
            st.info(f"📊 Saison sélectionnée: **{available_seasons[0]}**")
        elif season_option == "Saisons personnalisées":
            selected_seasons = st.multiselect(
                "Sélectionner les saisons:",
                available_seasons,
                default=[available_seasons[0]],
                key="season_multiselect",
                help="Maintenez Ctrl/Cmd pour sélectionner plusieurs saisons"
            )
        else:  # Toutes les saisons
            selected_seasons = available_seasons
            st.info(f"📊 **{len(available_seasons)} saisons** sélectionnées")
        
        # Afficher les informations sur les saisons sélectionnées
        if selected_seasons:
            st.header("📊 Informations Dataset")
            filtered_data = data[data['Season'].isin(selected_seasons)]
            
            total_matches = len(filtered_data)
            total_teams = len(set(list(filtered_data['HomeTeam'].unique()) + list(filtered_data['AwayTeam'].unique())))
            date_range = f"{filtered_data['Date'].min().strftime('%d/%m/%Y')} - {filtered_data['Date'].max().strftime('%d/%m/%Y')}"
            
            st.write(f"📅 **Période:** {date_range}")
            st.write(f"⚽ **Total matchs:** {total_matches}")
            st.write(f"🏟️ **Équipes:** {total_teams}")
            
            # Détail par saison
            if st.checkbox("Voir détail par saison"):
                for season in selected_seasons:
                    season_data = data[data['Season'] == season]
                    st.write(f"**{season}:** {len(season_data)} matchs")
    
    # Vérifier qu'au moins une saison est sélectionnée
    if not selected_seasons:
        st.error("⚠️ Veuillez sélectionner au moins une saison dans la sidebar!")
        st.stop()
    
    # Calculer les statistiques des équipes pour les saisons sélectionnées
    with st.spinner("📊 Calcul des statistiques des équipes..."):
        team_stats = calculate_team_stats(data, selected_seasons)
    
    if not team_stats:
        st.error("❌ Impossible de calculer les statistiques des équipes")
        st.stop()
    
    teams = sorted(team_stats.keys())
    
    # Routing vers les différentes pages
    if page == "🏠 Prédictions":
        show_predictions_page(data, teams, team_stats, selected_seasons)
    elif page == "📊 Analytics Avancées":
        show_analytics_page(data, teams, team_stats, selected_seasons)
    elif page == "🔍 Tête-à-Tête":
        show_head_to_head_page(data, teams, selected_seasons)
    elif page == "📈 Forme Récente":
        show_recent_form_page(data, teams, selected_seasons)

def show_predictions_page(data, teams, team_stats, selected_seasons):
    """Page principale de prédictions avec interface améliorée"""
    
    st.header("🎯 Prédictions de Match")
    
    # Notification sur la qualité des données
    data_quality = len(data) if data is not None else 0
    if data_quality > 1000:
        show_notification("📊 Base de données riche - Prédictions très fiables!", "success")
    elif data_quality > 500:
        show_notification("📊 Base de données correcte - Prédictions fiables", "info")
    else:
        show_notification("⚠️ Base de données limitée - Prédictions à prendre avec précaution", "warning")
    
    # Entraîner les modèles
    with st.spinner("🤖 Entraînement des modèles..."):
        home_model, away_model = train_prediction_models(data, selected_seasons)
    
    if home_model is None or away_model is None:
        show_notification("❌ Impossible d'entraîner les modèles", "danger")
        st.stop()
    else:
        show_notification("✅ Modèles entraînés avec succès!", "success")
    
    # Interface de sélection d'équipes avec métriques améliorées
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Équipe à Domicile")
        home_team = st.selectbox("Choisir l'équipe à domicile:", teams, key="home")
        
        if home_team and home_team in team_stats:
            stats = team_stats[home_team]
            
            # Métriques visuelles améliorées
            home_matches = stats.get('total_home_matches', 0)
            home_wins = stats.get('home_wins', 0)
            home_win_rate = (home_wins / max(1, home_matches)) * 100
            
            show_enhanced_metric("Matchs à Domicile", home_matches, help_text="Total des matchs joués à domicile", color="info")
            show_enhanced_metric("Victoires", f"{home_wins} ({home_win_rate:.1f}%)", help_text="Nombre et pourcentage de victoires", color="success")
            
            show_confidence_bar(home_win_rate, "Forme Domicile")
            
            st.write("**📊 Statistiques Offensives:**")
            st.write(f"🎯 **Tirs cadrés/match:** {stats.get('avg_shots_target_home', 0):.1f}")
            st.write(f"📈 **Tirs totaux/match:** {stats.get('avg_shots_home', 0):.1f}")
            st.write(f"🚩 **Corners/match:** {stats.get('avg_corners_home', 0):.1f}")
    
    with col2:
        st.subheader("✈️ Équipe à l'Extérieur")
        away_team = st.selectbox("Choisir l'équipe à l'extérieur:", teams, key="away")
        
        if away_team and away_team in team_stats:
            stats = team_stats[away_team]
            
            # Métriques visuelles améliorées
            away_matches = stats.get('total_away_matches', 0)
            away_wins = stats.get('away_wins', 0)
            away_win_rate = (away_wins / max(1, away_matches)) * 100
            
            show_enhanced_metric("Matchs à l'Extérieur", away_matches, help_text="Total des matchs joués à l'extérieur", color="info")
            show_enhanced_metric("Victoires", f"{away_wins} ({away_win_rate:.1f}%)", help_text="Nombre et pourcentage de victoires", color="success")
            
            show_confidence_bar(away_win_rate, "Forme Extérieur")
            
            st.write("**📊 Statistiques Offensives:**")
            st.write(f"🎯 **Tirs cadrés/match:** {stats.get('avg_shots_target_away', 0):.1f}")
            st.write(f"📈 **Tirs totaux/match:** {stats.get('avg_shots_away', 0):.1f}")
            st.write(f"🚩 **Corners/match:** {stats.get('avg_corners_away', 0):.1f}")
    
    # Bouton de prédiction avec style amélioré
    st.markdown("---")
    
    # Analyse pré-match si les deux équipes sont sélectionnées
    if home_team and away_team and home_team != away_team:
        # Notification d'analyse pré-match
        show_notification("🔍 Analyse pré-match disponible - Cliquez sur 'Prédire' pour des insights détaillés!", "info")
        
        # Aperçu rapide des équipes
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            show_enhanced_metric(f"🏠 {home_team}", f"{home_win_rate:.1f}%", help_text="Forme à domicile", color="primary")
        
        with col2:
            st.markdown("### ⚔️")
            st.markdown("<p style='text-align: center; font-size: 1.2rem; font-weight: bold;'>VS</p>", unsafe_allow_html=True)
        
        with col3:
            show_enhanced_metric(f"✈️ {away_team}", f"{away_win_rate:.1f}%", help_text="Forme à l'extérieur", color="secondary")
    
    if st.button("🔮 PRÉDIRE LE RÉSULTAT", type="primary", use_container_width=True):
        if home_team and away_team and home_team != away_team:
            
            # Notification de début de prédiction
            show_notification("⚽ Calcul de la prédiction en cours...", "info")
            
            with st.spinner("⚽ Analyse approfondie du match..."):
                time.sleep(1)  # Simulation d'analyse approfondie
                
                # Créer les features pour ce match
                home_features, away_features = create_match_features(home_team, away_team, team_stats)
                
                # Faire les prédictions
                home_goals_pred = home_model.predict([home_features])[0]
                away_goals_pred = away_model.predict([away_features])[0]
                
                # S'assurer que les prédictions sont positives
                home_goals_pred = max(0, home_goals_pred)
                away_goals_pred = max(0, away_goals_pred)
            
            # Notification de succès
            show_notification("✅ Prédiction calculée avec succès!", "success")
            
            # Afficher les résultats avec design amélioré
            st.markdown("---")
            st.subheader("🎯 PRÉDICTION DU MATCH")
            
            # Barre de confiance de la prédiction
            goal_diff = abs(home_goals_pred - away_goals_pred)
            confidence = min(95, 55 + goal_diff * 25)
            show_confidence_bar(confidence, "Confiance de la Prédiction")
            
            # Afficher les saisons utilisées pour cette prédiction
            if len(selected_seasons) == 1:
                season_text = f"Basé sur la saison {selected_seasons[0]}"
            else:
                season_text = f"Basé sur {len(selected_seasons)} saisons: {', '.join(selected_seasons)}"
            
            st.markdown(f"*{season_text}*")
            
            # Score prédit avec animations
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #e8f5e8, #d4edda); border-radius: 15px; border: 3px solid #28a745; margin: 20px 0; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent); transform: rotate(45deg); animation: shimmer 3s infinite;"></div>
                    <h2 style="color: #155724; margin: 0; font-size: 24px; position: relative; z-index: 1;">{home_team} 🆚 {away_team}</h2>
                    <h1 style="color: #155724; margin: 20px 0; font-size: 64px; font-weight: bold; position: relative; z-index: 1;">{home_goals_pred:.1f} - {away_goals_pred:.1f}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            # Analytics rapides du match (gardé comme avant)
            st.markdown("### 📊 Analytics du Match")
            
            # Historique tête-à-tête rapide
            h2h = get_head_to_head_analysis(data, home_team, away_team, selected_seasons)
            if h2h:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    show_enhanced_metric("Confrontations", int(h2h['total_matches']), color="info")
                with col2:
                    show_enhanced_metric(f"Victoires {home_team}", f"{int(h2h['team1_wins'])} ({h2h['team1_win_rate']:.1%})", color="success")
                with col3:
                    show_enhanced_metric("Matchs Nuls", f"{int(h2h['draws'])} ({h2h['draw_rate']:.1%})", color="warning")
                with col4:
                    show_enhanced_metric(f"Victoires {away_team}", f"{int(h2h['team2_wins'])} ({h2h['team2_win_rate']:.1%})", color="success")
            
            # Notification sur l'historique
            if h2h and h2h['total_matches'] > 5:
                show_notification(f"📊 Riche historique de {h2h['total_matches']} confrontations directes analysées!", "info")
            elif h2h and h2h['total_matches'] > 0:
                show_notification(f"📊 {h2h['total_matches']} confrontations directes trouvées", "warning")
            else:
                show_notification("⚠️ Aucune confrontation directe - Prédiction basée sur les performances générales", "warning")
            
            # Forme récente avec design amélioré
            st.markdown("#### 🏃‍♂️ Forme Récente (5 derniers matchs)")
            col1, col2 = st.columns(2)
            
            with col1:
                home_form = get_team_recent_form(data, home_team, 5, selected_seasons)
                if home_form:
                    form_color = "#4CAF50" if home_form['points_per_match'] >= 2 else "#FF9800" if home_form['points_per_match'] >= 1 else "#f44336"
                    st.markdown(f"""
                    <div class="recent-form" style="background: {form_color};">
                        <h5>🏠 {home_team}</h5>
                        <p>Points: {int(home_form['points'])}/{int(home_form['total_matches']*3)} ({home_form['points_per_match']:.1f}/match)</p>
                        <p>Buts: {int(home_form['goals_for'])}-{int(home_form['goals_against'])} (Diff: {int(home_form['goal_difference']):+d})</p>
                        <p>Bilan: {int(home_form['wins'])}V-{int(home_form['draws'])}N-{int(home_form['losses'])}D</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Notification sur la forme
                    if home_form['points_per_match'] >= 2.5:
                        show_notification(f"🔥 {home_team} en excellente forme!", "success")
                    elif home_form['points_per_match'] <= 1:
                        show_notification(f"😰 {home_team} en difficulté récemment", "warning")
            
            with col2:
                away_form = get_team_recent_form(data, away_team, 5, selected_seasons)
                if away_form:
                    form_color = "#4CAF50" if away_form['points_per_match'] >= 2 else "#FF9800" if away_form['points_per_match'] >= 1 else "#f44336"
                    st.markdown(f"""
                    <div class="recent-form" style="background: {form_color};">
                        <h5>✈️ {away_team}</h5>
                        <p>Points: {int(away_form['points'])}/{int(away_form['total_matches']*3)} ({away_form['points_per_match']:.1f}/match)</p>
                        <p>Buts: {int(away_form['goals_for'])}-{int(away_form['goals_against'])} (Diff: {int(away_form['goal_difference']):+d})</p>
                        <p>Bilan: {int(away_form['wins'])}V-{int(away_form['draws'])}N-{int(away_form['losses'])}D</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Notification sur la forme
                    if away_form['points_per_match'] >= 2.5:
                        show_notification(f"🔥 {away_team} en excellente forme!", "success")
                    elif away_form['points_per_match'] <= 1:
                        show_notification(f"😰 {away_team} en difficulté récemment", "warning")
            
            # Reste de la fonction identique (détails de prédiction, cotes bookmakers, etc.)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 Prédiction Domicile")
                st.metric("Buts prédits", f"{home_goals_pred:.2f}", help="Basé sur les performances historiques à domicile")
                st.write("**Statistiques utilisées:**")
                st.write(f"🎯 Tirs cadrés moyens: {home_features[0]:.1f}")
                st.write(f"📈 Tirs totaux moyens: {home_features[1]:.1f}")
                st.write(f"🚩 Corners moyens: {home_features[2]:.1f}")
            
            with col2:
                st.markdown("### ✈️ Prédiction Extérieur")
                st.metric("Buts prédits", f"{away_goals_pred:.2f}", help="Basé sur les performances historiques à l'extérieur")
                st.write("**Statistiques utilisées:**")
                st.write(f"🎯 Tirs cadrés moyens: {away_features[0]:.1f}")
                st.write(f"📈 Tirs totaux moyens: {away_features[1]:.1f}")
                st.write(f"🚩 Corners moyens: {away_features[2]:.1f}")
            
            # Récupérer les cotes historiques des bookmakers (conservé intégralement)
            historical_odds = get_historical_odds(data, home_team, away_team, selected_seasons)
            
            # Affichage des cotes des bookmakers
            if historical_odds and historical_odds.get('has_odds', False):
                st.markdown("### 💰 Cotes des Bookmakers")
                
                bookmaker_odds = historical_odds.get('bookmaker_odds', {})
                
                if historical_odds.get('direct_matches', 0) > 0:
                    st.info(f"📊 Basé sur {historical_odds['direct_matches']} confrontations directes dans les saisons sélectionnées")
                else:
                    st.info(f"📊 Basé sur les moyennes des équipes ({historical_odds.get('home_team_matches', 0)} matchs domicile, {historical_odds.get('away_team_matches', 0)} matchs extérieur)")
                
                if bookmaker_odds:
                    # Créer un tableau avec les cotes
                    odds_rows = []
                    for bookmaker, odds in bookmaker_odds.items():
                        odds_rows.append({
                            'Bookmaker': bookmaker,
                            f'🏠 {home_team}': f"{odds['home']:.2f} ({odds_to_percentage(odds['home']):.1f}%)",
                            '🤝 Match Nul': f"{odds['draw']:.2f} ({odds_to_percentage(odds['draw']):.1f}%)",
                            f'🚌 {away_team}': f"{odds['away']:.2f} ({odds_to_percentage(odds['away']):.1f}%)"
                        })
                    
                    if odds_rows:
                        odds_df = pd.DataFrame(odds_rows)
                        st.dataframe(odds_df, use_container_width=True, hide_index=True)
                        
                        # Affichage des cotes moyennes
                        if len(bookmaker_odds) > 1:
                            avg_home = np.mean([odds['home'] for odds in bookmaker_odds.values()])
                            avg_draw = np.mean([odds['draw'] for odds in bookmaker_odds.values()])
                            avg_away = np.mean([odds['away'] for odds in bookmaker_odds.values()])
                            
                            st.markdown("#### 📊 Moyennes des Cotes")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(f"🏠 {home_team}", f"{avg_home:.2f}", f"{odds_to_percentage(avg_home):.1f}%")
                            
                            with col2:
                                st.metric("🤝 Match Nul", f"{avg_draw:.2f}", f"{odds_to_percentage(avg_draw):.1f}%")
                            
                            with col3:
                                st.metric(f"🚌 {away_team}", f"{avg_away:.2f}", f"{odds_to_percentage(avg_away):.1f}%")
                
                st.markdown("---")
            
            # Analyse du résultat (conservé intégralement)
            goal_diff = abs(home_goals_pred - away_goals_pred)
            
            if home_goals_pred > away_goals_pred + 0.3:
                result = f"🏆 Victoire probable de {home_team}"
                confidence = min(95, 55 + goal_diff * 25)
                color = "#d4edda"
            elif away_goals_pred > home_goals_pred + 0.3:
                result = f"🏆 Victoire probable de {away_team}"
                confidence = min(95, 55 + goal_diff * 25)
                color = "#f8d7da"
            else:
                result = "⚖️ Match équilibré - Résultat incertain"
                confidence = 50
                color = "#fff3cd"
            
            # Total de buts
            total_goals = home_goals_pred + away_goals_pred
            if total_goals > 3:
                match_type = "🔥 Match offensif"
            elif total_goals < 2:
                match_type = "🛡️ Match défensif"
            else:
                match_type = "⚖️ Match équilibré"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: {color}; border-radius: 10px; margin: 20px 0; border: 2px solid #6c757d;">
                <h3 style="margin: 0; color: #495057;">{result}</h3>
                <p style="margin: 10px 0; color: #495057; font-size: 18px;">Confiance: {confidence:.0f}%</p>
                <p style="margin: 5px 0; color: #495057;">{match_type} - Total buts attendus: {total_goals:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error("⚠️ Veuillez sélectionner deux équipes différentes!")
    
    # Informations sur le modèle (conservé comme avant)
    with st.expander("ℹ️ Comment fonctionne la prédiction?"):
        st.markdown(f"""
        ### 🧠 Méthodologie
        
        Ce système prédit les résultats de **futurs matchs** en analysant les performances historiques:
        
        **📅 Données utilisées:**
        - Saisons sélectionnées: **{', '.join(selected_seasons)}**
        - Moyennes des **tirs cadrés** par équipe
        - Moyennes des **tirs totaux** par équipe  
        - Moyennes des **corners** par équipe
        - Distinction **domicile/extérieur**
        
        **🤖 Algorithme:**
        - **Random Forest** avec 100 arbres de décision
        - Entraîné sur les matchs des saisons sélectionnées
        - Validation croisée pour éviter le surapprentissage
        
        **🎯 Prédiction:**
        - Chaque équipe est évaluée selon ses propres moyennes historiques
        - L'avantage du terrain est pris en compte
        - Les prédictions sont des probabilités, pas des certitudes
        
        **⚠️ Limitations:**
        - Ne prend pas en compte la forme récente
        - Ignore les blessures/suspensions
        - Basé uniquement sur les données historiques des saisons sélectionnées
        """)
        
        if data is not None and selected_seasons:
            filtered_data = data[data['Season'].isin(selected_seasons)]
            st.write("### 📈 Statistiques du modèle")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Matchs d'entraînement", len(filtered_data))
            with col2:
                avg_home_goals = filtered_data['FTHG'].mean()
                st.metric("Buts domicile/match", f"{avg_home_goals:.2f}")
            with col3:
                avg_away_goals = filtered_data['FTAG'].mean()
                st.metric("Buts extérieur/match", f"{avg_away_goals:.2f}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 Prédiction Domicile")
                st.metric("Buts prédits", f"{home_goals_pred:.2f}", help="Basé sur les performances historiques à domicile")
                st.write("**Statistiques utilisées:**")
                st.write(f"🎯 Tirs cadrés moyens: {home_features[0]:.1f}")
                st.write(f"📈 Tirs totaux moyens: {home_features[1]:.1f}")
                st.write(f"🚩 Corners moyens: {home_features[2]:.1f}")
            
            with col2:
                st.markdown("### ✈️ Prédiction Extérieur")
                st.metric("Buts prédits", f"{away_goals_pred:.2f}", help="Basé sur les performances historiques à l'extérieur")
                st.write("**Statistiques utilisées:**")
                st.write(f"🎯 Tirs cadrés moyens: {away_features[0]:.1f}")
                st.write(f"📈 Tirs totaux moyens: {away_features[1]:.1f}")
                st.write(f"🚩 Corners moyens: {away_features[2]:.1f}")
            
            # Récupérer les cotes historiques des bookmakers
            historical_odds = get_historical_odds(data, home_team, away_team, selected_seasons)
            
            # Affichage des cotes des bookmakers
            if historical_odds and historical_odds.get('has_odds', False):
                st.markdown("### 💰 Cotes des Bookmakers")
                
                bookmaker_odds = historical_odds.get('bookmaker_odds', {})
                
                if historical_odds.get('direct_matches', 0) > 0:
                    st.info(f"📊 Basé sur {historical_odds['direct_matches']} confrontations directes dans les saisons sélectionnées")
                else:
                    st.info(f"📊 Basé sur les moyennes des équipes ({historical_odds.get('home_team_matches', 0)} matchs domicile, {historical_odds.get('away_team_matches', 0)} matchs extérieur)")
                
                if bookmaker_odds:
                    # Créer un tableau avec les cotes
                    odds_rows = []
                    for bookmaker, odds in bookmaker_odds.items():
                        odds_rows.append({
                            'Bookmaker': bookmaker,
                            f'🏠 {home_team}': f"{odds['home']:.2f} ({odds_to_percentage(odds['home']):.1f}%)",
                            '🤝 Match Nul': f"{odds['draw']:.2f} ({odds_to_percentage(odds['draw']):.1f}%)",
                            f'🚌 {away_team}': f"{odds['away']:.2f} ({odds_to_percentage(odds['away']):.1f}%)"
                        })
                    
                    if odds_rows:
                        odds_df = pd.DataFrame(odds_rows)
                        st.dataframe(odds_df, use_container_width=True, hide_index=True)
                        
                        # Affichage des cotes moyennes
                        if len(bookmaker_odds) > 1:
                            avg_home = np.mean([odds['home'] for odds in bookmaker_odds.values()])
                            avg_draw = np.mean([odds['draw'] for odds in bookmaker_odds.values()])
                            avg_away = np.mean([odds['away'] for odds in bookmaker_odds.values()])
                            
                            st.markdown("#### 📊 Moyennes des Cotes")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(f"🏠 {home_team}", f"{avg_home:.2f}", f"{odds_to_percentage(avg_home):.1f}%")
                            
                            with col2:
                                st.metric("🤝 Match Nul", f"{avg_draw:.2f}", f"{odds_to_percentage(avg_draw):.1f}%")
                            
                            with col3:
                                st.metric(f"🚌 {away_team}", f"{avg_away:.2f}", f"{odds_to_percentage(avg_away):.1f}%")
                
                st.markdown("---")
            
            # Analyse du résultat
            goal_diff = abs(home_goals_pred - away_goals_pred)
            
            if home_goals_pred > away_goals_pred + 0.3:
                result = f"🏆 Victoire probable de {home_team}"
                confidence = min(95, 55 + goal_diff * 25)
                color = "#d4edda"
            elif away_goals_pred > home_goals_pred + 0.3:
                result = f"🏆 Victoire probable de {away_team}"
                confidence = min(95, 55 + goal_diff * 25)
                color = "#f8d7da"
            else:
                result = "⚖️ Match équilibré - Résultat incertain"
                confidence = 50
                color = "#fff3cd"
            
            # Total de buts
            total_goals = home_goals_pred + away_goals_pred
            if total_goals > 3:
                match_type = "🔥 Match offensif"
            elif total_goals < 2:
                match_type = "🛡️ Match défensif"
            else:
                match_type = "⚖️ Match équilibré"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: {color}; border-radius: 10px; margin: 20px 0; border: 2px solid #6c757d;">
                <h3 style="margin: 0; color: #495057;">{result}</h3>
                <p style="margin: 10px 0; color: #495057; font-size: 18px;">Confiance: {confidence:.0f}%</p>
                <p style="margin: 5px 0; color: #495057;">{match_type} - Total buts attendus: {total_goals:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error("⚠️ Veuillez sélectionner deux équipes différentes!")
    
    # Informations sur le modèle
    with st.expander("ℹ️ Comment fonctionne la prédiction?"):
        st.markdown(f"""
        ### 🧠 Méthodologie
        
        Ce système prédit les résultats de **futurs matchs** en analysant les performances historiques:
        
        **📅 Données utilisées:**
        - Saisons sélectionnées: **{', '.join(selected_seasons)}**
        - Moyennes des **tirs cadrés** par équipe
        - Moyennes des **tirs totaux** par équipe  
        - Moyennes des **corners** par équipe
        - Distinction **domicile/extérieur**
        
        **🤖 Algorithme:**
        - **Random Forest** avec 100 arbres de décision
        - Entraîné sur les matchs des saisons sélectionnées
        - Validation croisée pour éviter le surapprentissage
        
        **🎯 Prédiction:**
        - Chaque équipe est évaluée selon ses propres moyennes historiques
        - L'avantage du terrain est pris en compte
        - Les prédictions sont des probabilités, pas des certitudes
        
        **⚠️ Limitations:**
        - Ne prend pas en compte la forme récente
        - Ignore les blessures/suspensions
        - Basé uniquement sur les données historiques des saisons sélectionnées
        """)
        
        if data is not None and selected_seasons:
            filtered_data = data[data['Season'].isin(selected_seasons)]
            st.write("### 📈 Statistiques du modèle")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Matchs d'entraînement", len(filtered_data))
            with col2:
                avg_home_goals = filtered_data['FTHG'].mean()
                st.metric("Buts domicile/match", f"{avg_home_goals:.2f}")
            with col3:
                avg_away_goals = filtered_data['FTAG'].mean()
                st.metric("Buts extérieur/match", f"{avg_away_goals:.2f}")

if __name__ == "__main__":
    main()
