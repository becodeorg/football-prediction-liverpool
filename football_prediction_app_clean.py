"""
🚀 FOOTBALL PREDICTION APP - VERSION ULTRA PROPRE
=================================================
Application de prédiction football sans bugs - Version nettoyée
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="⚽ Football Prediction V4.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Ultra Propre
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Chargement des données football"""
    try:
        # Essayer différents encodages
        encodings = ['latin-1', 'utf-8', 'cp1252']
        data = None
        
        for encoding in encodings:
            try:
                data = pd.read_csv('dataset.csv', encoding=encoding)
                break
            except:
                continue
        
        if data is None:
            st.error("❌ Impossible de charger le fichier dataset.csv")
            return None
        
        # Nettoyer et formater les données
        data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d', errors='coerce')
        data = data.dropna(subset=['Date'])
        
        # Calculer la saison (Juillet à Juin)
        data['Season'] = data['Date'].apply(lambda x: f"{x.year}-{x.year+1}" if x.month >= 7 else f"{x.year-1}-{x.year}")
        
        return data
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
        return None

def calculate_team_stats(data, seasons):
    """Calcul des statistiques des équipes - Version Simplifiée"""
    if data is None or len(data) == 0:
        return {}
    
    season_data = data[data['Season'].isin(seasons)]
    team_stats = {}
    
    # Obtenir toutes les équipes uniques
    all_teams = set(season_data['HomeTeam'].unique()) | set(season_data['AwayTeam'].unique())
    
    for team in all_teams:
        # Matchs à domicile
        home_matches = season_data[season_data['HomeTeam'] == team]
        home_wins = len(home_matches[home_matches['FTR'] == 'H'])
        home_goals = home_matches['FTHG'].mean() if len(home_matches) > 0 else 0
        
        # Matchs à l'extérieur
        away_matches = season_data[season_data['AwayTeam'] == team]
        away_wins = len(away_matches[away_matches['FTR'] == 'A'])
        away_goals = away_matches['FTAG'].mean() if len(away_matches) > 0 else 0
        
        team_stats[team] = {
            'total_home_matches': len(home_matches),
            'home_wins': home_wins,
            'home_win_rate': home_wins / len(home_matches) if len(home_matches) > 0 else 0,
            'avg_goals_home': home_goals,
            'total_away_matches': len(away_matches),
            'away_wins': away_wins,
            'away_win_rate': away_wins / len(away_matches) if len(away_matches) > 0 else 0,
            'avg_goals_away': away_goals
        }
    
    return team_stats

def show_metric_card(title, value, subtitle):
    """Affichage d'une métrique propre"""
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #667eea;">{title}</h3>
        <h2 style="margin: 0.5rem 0; color: #333;">{value}</h2>
        <p style="margin: 0; color: #666;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def predict_match(home_team, away_team, team_stats):
    """Prédiction simple d'un match"""
    if home_team not in team_stats or away_team not in team_stats:
        return None, None, 0
    
    # Calcul simple basé sur les moyennes
    home_avg = team_stats[home_team]['avg_goals_home']
    away_avg = team_stats[away_team]['avg_goals_away']
    
    # Ajouter un peu de randomness
    home_pred = max(0, home_avg + np.random.normal(0, 0.3))
    away_pred = max(0, away_avg + np.random.normal(0, 0.3))
    
    # Calcul de confiance
    goal_diff = abs(home_pred - away_pred)
    confidence = min(90, 50 + goal_diff * 30)
    
    return home_pred, away_pred, confidence

def show_prediction_interface(data, selected_seasons, team_stats, teams):
    """Interface de prédiction principale - PROPRE"""
    st.markdown("---")
    st.markdown("## 🎯 Prédiction de Match")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Équipe à Domicile")
        home_team = st.selectbox("Sélectionner:", teams, key="home_clean")
        
        if home_team and home_team in team_stats:
            stats = team_stats[home_team]
            st.info(f"📊 Victoires domicile: {stats['home_wins']}/{stats['total_home_matches']} ({stats['home_win_rate']*100:.1f}%)")
    
    with col2:
        st.markdown("### ✈️ Équipe à l'Extérieur")
        away_team = st.selectbox("Sélectionner:", teams, key="away_clean")
        
        if away_team and away_team in team_stats:
            stats = team_stats[away_team]
            st.info(f"📊 Victoires extérieur: {stats['away_wins']}/{stats['total_away_matches']} ({stats['away_win_rate']*100:.1f}%)")
    
    # Bouton de prédiction
    if st.button("🔮 PRÉDIRE LE MATCH", type="primary"):
        if home_team and away_team and home_team != away_team:
            with st.spinner("🤖 Calcul en cours..."):
                time.sleep(1)
                
                home_pred, away_pred, confidence = predict_match(home_team, away_team, team_stats)
                
                if home_pred is not None:
                    st.markdown("---")
                    st.markdown("### 🏆 Résultat de la Prédiction")
                    
                    # Affichage du score
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); 
                                    padding: 2rem; border-radius: 15px; color: white; margin: 1rem 0;">
                            <h3>{home_team} 🆚 {away_team}</h3>
                            <h1 style="font-size: 3rem; margin: 1rem 0;">{home_pred:.1f} - {away_pred:.1f}</h1>
                            <p>Confiance: {confidence:.0f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Analyse du résultat
                    if home_pred > away_pred + 0.5:
                        st.success(f"🏆 Victoire probable de {home_team}")
                    elif away_pred > home_pred + 0.5:
                        st.success(f"🏆 Victoire probable de {away_team}")
                    else:
                        st.warning("⚖️ Match équilibré - Résultat incertain")
                
                else:
                    st.error("❌ Impossible de calculer la prédiction")
        else:
            st.error("⚠️ Veuillez sélectionner deux équipes différentes")

def show_bookmaker_odds(data, teams):
    """Affichage des cotes bookmakers - VERSION ULTRA SIMPLE"""
    st.markdown("---")
    st.markdown("## 💰 Cotes des Bookmakers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("Équipe domicile:", teams, key="odds_home")
    
    with col2:
        away_team = st.selectbox("Équipe extérieur:", teams, key="odds_away")
    
    if st.button("💰 VOIR LES COTES", type="primary"):
        if home_team and away_team and home_team != away_team:
            # Recherche des matchs historiques
            historical_matches = data[
                ((data['HomeTeam'] == home_team) & (data['AwayTeam'] == away_team)) |
                ((data['HomeTeam'] == away_team) & (data['AwayTeam'] == home_team))
            ]
            
            if len(historical_matches) > 0:
                st.success(f"✅ {len(historical_matches)} match(s) trouvé(s)")
                
                # Afficher les 3 derniers matchs
                recent_matches = historical_matches.tail(3)
                
                for idx, (_, match) in enumerate(recent_matches.iterrows()):
                    with st.expander(f"🏆 Match {idx+1} - {match['Date'].strftime('%d/%m/%Y')} - {match['HomeTeam']} vs {match['AwayTeam']}"):
                        
                        # Score
                        st.write(f"⚽ **Score:** {int(match['FTHG'])}-{int(match['FTAG'])}")
                        
                        # Cotes si disponibles
                        cotes_affichees = False
                        
                        if pd.notna(match.get('B365H')) and match.get('B365H', 0) > 0:
                            st.write(f"🟢 **Bet365:** Dom {match['B365H']:.2f} | Nul {match.get('B365D', 0):.2f} | Ext {match.get('B365A', 0):.2f}")
                            cotes_affichees = True
                        
                        if pd.notna(match.get('BWH')) and match.get('BWH', 0) > 0:
                            st.write(f"🔵 **Betway:** Dom {match['BWH']:.2f} | Nul {match.get('BWD', 0):.2f} | Ext {match.get('BWA', 0):.2f}")
                            cotes_affichees = True
                        
                        if not cotes_affichees:
                            st.warning("⚠️ Aucune cote disponible")
            else:
                st.error(f"❌ Aucun match trouvé entre {home_team} et {away_team}")
        else:
            st.error("⚠️ Sélectionnez deux équipes différentes")

def main():
    """Fonction principale - VERSION PROPRE"""
    
    # En-tête
    st.markdown("""
    <div class="main-header">
        <h1>⚽ Football Prediction V4.0 - CLEAN</h1>
        <p>🚀 Version Ultra Propre Sans Bugs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chargement des données
    with st.spinner("📊 Chargement des données..."):
        data = load_data()
    
    if data is None:
        st.stop()
    
    st.success(f"✅ {len(data)} matchs chargés avec succès!")
    
    # Sidebar pour sélection des saisons
    st.sidebar.markdown("## 📅 Configuration")
    available_seasons = sorted(data['Season'].unique())
    selected_seasons = st.sidebar.multiselect(
        "Saisons à analyser:",
        available_seasons,
        default=available_seasons[-2:] if len(available_seasons) >= 2 else available_seasons
    )
    
    if not selected_seasons:
        st.warning("⚠️ Veuillez sélectionner au moins une saison")
        st.stop()
    
    # Calcul des statistiques
    with st.spinner("📊 Calcul des statistiques..."):
        team_stats = calculate_team_stats(data, selected_seasons)
        teams = sorted(team_stats.keys())
    
    # Métriques générales
    st.markdown("### 📊 Aperçu des Données")
    col1, col2, col3, col4 = st.columns(4)
    
    season_data = data[data['Season'].isin(selected_seasons)]
    
    with col1:
        show_metric_card("Matchs", len(season_data), "Total analysés")
    
    with col2:
        show_metric_card("Équipes", len(teams), "Dans la base")
    
    with col3:
        show_metric_card("Saisons", len(selected_seasons), "Sélectionnées")
    
    with col4:
        avg_goals = season_data[['FTHG', 'FTAG']].mean().mean()
        show_metric_card("Buts/Match", f"{avg_goals:.1f}", "Moyenne")
    
    # Navigation simple
    st.sidebar.markdown("---")
    view = st.sidebar.radio(
        "🎯 Fonctionnalités:",
        ["🔮 Prédiction", "💰 Cotes Bookmakers"]
    )
    
    # Affichage selon la vue
    if view == "🔮 Prédiction":
        show_prediction_interface(data, selected_seasons, team_stats, teams)
    elif view == "💰 Cotes Bookmakers":
        show_bookmaker_odds(data, teams)

if __name__ == "__main__":
    main()
