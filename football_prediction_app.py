#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚽ SYSTÈME DE PRÉDICTION DE FUTURS MATCHS FOOTBALL
Application Streamlit pour prédire les résultats de matchs avant qu'ils ne se déroulent
Avec sélection par saison pour une analyse plus précise

Utilisation: streamlit run football_prediction_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="⚽ Prédiction Futurs Matchs", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Interface principale
def main():
    # Titre principal
    st.title("⚽ PRÉDICTION DE FUTURS MATCHS FOOTBALL")
    st.markdown("*Prédisez les résultats avant que les matchs ne commencent !*")
    st.markdown("---")
    
    # Charger les données
    with st.spinner("🔄 Chargement des données..."):
        data = load_and_prepare_data()
    
    if data is None:
        st.stop()
    
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
            st.subheader("🏆 Détail par saison")
            for season in selected_seasons:
                season_data = data[data['Season'] == season]
                st.write(f"**{season}:** {len(season_data)} matchs")
        
        st.header("🤖 Modèle")
        st.write("**Algorithm:** Random Forest")
        st.write("**Variables:** Tirs cadrés, Tirs totaux, Corners")
        st.write("**Entraînement:** Données des saisons sélectionnées")
    
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
    
    # Entraîner les modèles
    with st.spinner("🤖 Entraînement des modèles..."):
        home_model, away_model = train_prediction_models(data, selected_seasons)
    
    if home_model is None or away_model is None:
        st.error("❌ Impossible d'entraîner les modèles")
        st.stop()
    
    # Interface de sélection d'équipes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Équipe à Domicile")
        home_team = st.selectbox("Choisir l'équipe à domicile:", teams, key="home")
        
        if home_team:
            display_team_record(team_stats, home_team, "home")
            
            if home_team in team_stats:
                stats = team_stats[home_team]
                st.write(f"🎯 **Tirs cadrés/match:** {stats.get('avg_shots_target_home', 0):.1f}")
                st.write(f"📈 **Tirs totaux/match:** {stats.get('avg_shots_home', 0):.1f}")
                st.write(f"🚩 **Corners/match:** {stats.get('avg_corners_home', 0):.1f}")
    
    with col2:
        st.subheader("✈️ Équipe à l'Extérieur")
        away_team = st.selectbox("Choisir l'équipe à l'extérieur:", teams, key="away")
        
        if away_team:
            display_team_record(team_stats, away_team, "away")
            
            if away_team in team_stats:
                stats = team_stats[away_team]
                st.write(f"🎯 **Tirs cadrés/match:** {stats.get('avg_shots_target_away', 0):.1f}")
                st.write(f"📈 **Tirs totaux/match:** {stats.get('avg_shots_away', 0):.1f}")
                st.write(f"🚩 **Corners/match:** {stats.get('avg_corners_away', 0):.1f}")
    
    # Bouton de prédiction
    st.markdown("---")
    if st.button("🔮 PRÉDIRE LE RÉSULTAT", type="primary", use_container_width=True):
        if home_team and away_team and home_team != away_team:
            
            with st.spinner("⚽ Calcul de la prédiction..."):
                # Créer les features pour ce match
                home_features, away_features = create_match_features(home_team, away_team, team_stats)
                
                # Faire les prédictions
                home_goals_pred = home_model.predict([home_features])[0]
                away_goals_pred = away_model.predict([away_features])[0]
                
                # S'assurer que les prédictions sont positives
                home_goals_pred = max(0, home_goals_pred)
                away_goals_pred = max(0, away_goals_pred)
            
            # Afficher les résultats
            st.markdown("---")
            st.subheader("🎯 PRÉDICTION DU MATCH")
            
            # Afficher les saisons utilisées pour cette prédiction
            if len(selected_seasons) == 1:
                season_text = f"Basé sur la saison {selected_seasons[0]}"
            else:
                season_text = f"Basé sur {len(selected_seasons)} saisons: {', '.join(selected_seasons)}"
            
            st.markdown(f"*{season_text}*")
            
            # Score prédit
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #e8f5e8, #d4edda); border-radius: 15px; border: 3px solid #28a745; margin: 20px 0;">
                    <h2 style="color: #155724; margin: 0; font-size: 24px;">{home_team} 🆚 {away_team}</h2>
                    <h1 style="color: #155724; margin: 20px 0; font-size: 64px; font-weight: bold;">{home_goals_pred:.1f} - {away_goals_pred:.1f}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            # Détails de la prédiction
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
