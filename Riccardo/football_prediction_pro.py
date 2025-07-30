#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚽ SYSTÈME DE PRÉDICTION FOOTBALL - VERSION AMÉLIORÉE
Application Streamlit avec dashboard professionnel et fonctionnalités avancées

Nouvelles fonctionnalités:
- Dashboard avec métriques en temps réel  
- Graphiques interactifs avec Plotly
- Système de confiance des prédictions
- Analyse de forme récente des équipes
- Comparaison avec les cotes
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Configuration avancée de la page
st.set_page_config(
    page_title="⚽ Football Prediction Pro", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pour un design plus professionnel
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .prediction-card {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    
    .confidence-high { color: #4CAF50; font-weight: bold; }
    .confidence-medium { color: #FF9800; font-weight: bold; }
    .confidence-low { color: #f44336; font-weight: bold; }
    
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def get_season_from_date(date):
    """Détermine la saison footballistique à partir d'une date"""
    year = date.year
    month = date.month
    
    if month >= 7:  # Juillet à décembre
        return f"{year}-{str(year+1)[2:]}"
    else:  # Janvier à juin
        return f"{year-1}-{str(year)[2:]}"

@st.cache_data
def load_and_prepare_data():
    """Charger le dataset et ajouter les informations de saison"""
    try:
        data = pd.read_csv('dataset.csv')
        data['Date'] = pd.to_datetime(data['Date'], format='mixed', dayfirst=True)
        data['Season'] = data['Date'].apply(get_season_from_date)
        return data
        
    except FileNotFoundError:
        st.error("❌ Fichier 'dataset.csv' non trouvé.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {str(e)}")
        return None

def calculate_team_form(data, team_name, num_matches=5):
    """Calculer la forme récente d'une équipe"""
    team_matches = data[
        (data['HomeTeam'] == team_name) | (data['AwayTeam'] == team_name)
    ].sort_values('Date', ascending=False).head(num_matches)
    
    if len(team_matches) == 0:
        return {"wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "form": "N/A"}
    
    wins = draws = losses = goals_for = goals_against = 0
    
    for _, match in team_matches.iterrows():
        if match['HomeTeam'] == team_name:
            goals_for += match['FTHG']
            goals_against += match['FTAG']
            if match['FTR'] == 'H':
                wins += 1
            elif match['FTR'] == 'D':
                draws += 1
            else:
                losses += 1
        else:
            goals_for += match['FTAG']
            goals_against += match['FTHG']
            if match['FTR'] == 'A':
                wins += 1
            elif match['FTR'] == 'D':
                draws += 1
            else:
                losses += 1
    
    # Calcul du score de forme (3 points victoire, 1 point nul)
    points = wins * 3 + draws
    max_points = len(team_matches) * 3
    form_percentage = (points / max_points * 100) if max_points > 0 else 0
    
    return {
        "wins": wins,
        "draws": draws, 
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "form_percentage": form_percentage,
        "total_matches": len(team_matches)
    }

def create_form_chart(home_form, away_form, home_team, away_team):
    """Créer un graphique de comparaison de forme"""
    fig = go.Figure()
    
    categories = ['Victoires', 'Matchs Nuls', 'Défaites']
    
    fig.add_trace(go.Bar(
        name=home_team,
        x=categories,
        y=[home_form['wins'], home_form['draws'], home_form['losses']],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name=away_team,
        x=categories,
        y=[away_form['wins'], away_form['draws'], away_form['losses']],
        marker_color='lightcoral'
    ))
    
    fig.update_layout(
        title="🔥 Forme Récente (5 derniers matchs)",
        xaxis_title="Résultats",
        yaxis_title="Nombre de matchs",
        barmode='group'
    )
    
    return fig

def predict_match_advanced(data, home_team, away_team, selected_seasons=None):
    """Prédiction avancée avec système de confiance"""
    # Filtrer par saison si spécifié
    if selected_seasons:
        filtered_data = data[data['Season'].isin(selected_seasons)]
    else:
        filtered_data = data
    
    # Préparer les données d'entraînement avec plus de features
    clean_data = filtered_data.dropna(subset=['HST', 'AST', 'HS', 'AS', 'HC', 'AC', 'FTHG', 'FTAG'])
    
    if len(clean_data) < 50:  # Minimum de données requis
        return None
    
    # Features enrichies
    X_home = clean_data[['HST', 'HS', 'HC']].values
    y_home = clean_data['FTHG'].values
    
    X_away = clean_data[['AST', 'AS', 'AC']].values  
    y_away = clean_data['FTAG'].values
    
    # Utiliser Gradient Boosting pour de meilleures performances
    home_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    away_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    
    # Validation croisée pour calculer la confiance
    X_home_train, X_home_test, y_home_train, y_home_test = train_test_split(
        X_home, y_home, test_size=0.2, random_state=42
    )
    X_away_train, X_away_test, y_away_train, y_away_test = train_test_split(
        X_away, y_away, test_size=0.2, random_state=42
    )
    
    home_model.fit(X_home_train, y_home_train)
    away_model.fit(X_away_train, y_away_train)
    
    # Calculer les métriques de performance
    home_pred_test = home_model.predict(X_home_test)
    away_pred_test = away_model.predict(X_away_test)
    
    home_r2 = r2_score(y_home_test, home_pred_test)
    away_r2 = r2_score(y_away_test, away_pred_test)
    
    # Calculer la confiance basée sur le R²
    confidence = (home_r2 + away_r2) / 2 * 100
    confidence = max(0, min(100, confidence))  # Limiter entre 0 et 100
    
    return {
        'home_model': home_model,
        'away_model': away_model,
        'confidence': confidence,
        'home_r2': home_r2,
        'away_r2': away_r2
    }

def get_confidence_class(confidence):
    """Retourner la classe CSS selon le niveau de confiance"""
    if confidence >= 70:
        return "confidence-high"
    elif confidence >= 50:
        return "confidence-medium"
    else:
        return "confidence-low"

def main():
    # En-tête principal
    st.markdown('<h1 class="main-header">⚽ Football Prediction Pro</h1>', unsafe_allow_html=True)
    
    # Charger les données
    data = load_and_prepare_data()
    if data is None:
        st.stop()
    
    # Sidebar pour la configuration
    st.sidebar.title("🎛️ Configuration")
    
    # Sélection des saisons
    available_seasons = sorted(data['Season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "📅 Sélectionner les saisons pour l'entraînement:",
        options=available_seasons,
        default=available_seasons[-2:],  # 2 dernières saisons par défaut
        help="Choisissez les saisons pour entraîner le modèle"
    )
    
    # Sélection des équipes
    teams = sorted(set(list(data['HomeTeam'].unique()) + list(data['AwayTeam'].unique())))
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Équipe à Domicile:", teams, index=0)
    
    with col2:
        away_team = st.selectbox("✈️ Équipe à l'Extérieur:", teams, 
                                index=1 if len(teams) > 1 else 0)
    
    if home_team == away_team:
        st.warning("⚠️ Veuillez sélectionner deux équipes différentes")
        return
    
    # Bouton de prédiction
    if st.button("🔮 PRÉDIRE LE MATCH", key="predict_btn"):
        with st.spinner("🤖 Analyse en cours..."):
            
            # Calculer la forme récente
            home_form = calculate_team_form(data, home_team)
            away_form = calculate_team_form(data, away_team)
            
            # Prédiction avancée
            prediction_result = predict_match_advanced(data, home_team, away_team, selected_seasons)
            
            if prediction_result is None:
                st.error("❌ Pas assez de données pour effectuer une prédiction fiable")
                return
            
            # Affichage des métriques de forme
            st.subheader("📊 Dashboard - Vue d'ensemble")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🏠 {home_team}</h3>
                    <p>Forme: {home_form['form_percentage']:.1f}%</p>
                    <p>{home_form['wins']}V-{home_form['draws']}N-{home_form['losses']}D</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>✈️ {away_team}</h3>
                    <p>Forme: {away_form['form_percentage']:.1f}%</p>
                    <p>{away_form['wins']}V-{away_form['draws']}N-{away_form['losses']}D</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                confidence = prediction_result['confidence']
                confidence_class = get_confidence_class(confidence)
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎯 Confiance</h3>
                    <p class="{confidence_class}">{confidence:.1f}%</p>
                    <p>Modèle: {"Excellent" if confidence >= 70 else "Bon" if confidence >= 50 else "Moyen"}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                total_matches = len(data[data['Season'].isin(selected_seasons)])
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 Données</h3>
                    <p>{total_matches} matchs</p>
                    <p>{len(selected_seasons)} saisons</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Graphique de forme
            st.plotly_chart(create_form_chart(home_form, away_form, home_team, away_team), use_container_width=True)
            
            # Prédiction du match
            st.subheader("🔮 Prédiction du Match")
            
            # Estimer les statistiques moyennes pour la prédiction
            home_stats = data[data['HomeTeam'] == home_team].mean()
            away_stats = data[data['AwayTeam'] == away_team].mean()
            
            # Utiliser les moyennes ou des valeurs par défaut
            home_hst = home_stats.get('HST', 5) if not pd.isna(home_stats.get('HST', 5)) else 5
            home_hs = home_stats.get('HS', 12) if not pd.isna(home_stats.get('HS', 12)) else 12
            home_hc = home_stats.get('HC', 6) if not pd.isna(home_stats.get('HC', 6)) else 6
            
            away_ast = away_stats.get('AST', 4) if not pd.isna(away_stats.get('AST', 4)) else 4
            away_as = away_stats.get('AS', 10) if not pd.isna(away_stats.get('AS', 10)) else 10
            away_ac = away_stats.get('AC', 5) if not pd.isna(away_stats.get('AC', 5)) else 5
            
            # Ajustement basé sur la forme récente
            form_factor_home = home_form['form_percentage'] / 50  # Normaliser autour de 1
            form_factor_away = away_form['form_percentage'] / 50
            
            home_hst *= form_factor_home
            home_hs *= form_factor_home
            away_ast *= form_factor_away
            away_as *= form_factor_away
            
            # Prédire les buts
            home_goals = prediction_result['home_model'].predict([[home_hst, home_hs, home_hc]])[0]
            away_goals = prediction_result['away_model'].predict([[away_ast, away_as, away_ac]])[0]
            
            # S'assurer que les buts sont positifs et réalistes
            home_goals = max(0, round(home_goals, 1))
            away_goals = max(0, round(away_goals, 1))
            
            # Déterminer le résultat
            if home_goals > away_goals:
                result = "Victoire Domicile"
                result_emoji = "🏠"
                result_color = "success"
            elif away_goals > home_goals:
                result = "Victoire Extérieur"
                result_emoji = "✈️"
                result_color = "info"
            else:
                result = "Match Nul"
                result_emoji = "🤝"
                result_color = "warning"
            
            # Affichage de la prédiction
            st.markdown(f"""
            <div class="prediction-card">
                <h2 style="text-align: center;">{result_emoji} {result}</h2>
                <h1 style="text-align: center; font-size: 3rem;">
                    {home_team} {home_goals:.1f} - {away_goals:.1f} {away_team}
                </h1>
                <p style="text-align: center;">
                    <span class="{get_confidence_class(confidence)}">Confiance: {confidence:.1f}%</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Détails supplémentaires
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"🏠 {home_team} - Détails")
                st.write(f"⚽ Buts prédits: {home_goals:.1f}")
                st.write(f"🎯 Tirs cadrés estimés: {home_hst:.1f}")
                st.write(f"🏹 Tirs totaux estimés: {home_hs:.1f}")
                st.write(f"📈 Forme récente: {home_form['form_percentage']:.1f}%")
                st.write(f"⚽ Buts récents: {home_form['goals_for']}/{home_form['goals_against']}")
            
            with col2:
                st.subheader(f"✈️ {away_team} - Détails")
                st.write(f"⚽ Buts prédits: {away_goals:.1f}")
                st.write(f"🎯 Tirs cadrés estimés: {away_ast:.1f}")
                st.write(f"🏹 Tirs totaux estimés: {away_as:.1f}")
                st.write(f"📈 Forme récente: {away_form['form_percentage']:.1f}%")
                st.write(f"⚽ Buts récents: {away_form['goals_for']}/{away_form['goals_against']}")
            
            # Métriques du modèle
            with st.expander("🔧 Métriques du Modèle"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"📊 R² Domicile: {prediction_result['home_r2']:.3f}")
                    st.write(f"📊 R² Extérieur: {prediction_result['away_r2']:.3f}")
                with col2:
                    st.write(f"🎯 Confiance globale: {confidence:.1f}%")
                    st.write(f"📈 Saisons utilisées: {len(selected_seasons)}")

if __name__ == "__main__":
    main()
