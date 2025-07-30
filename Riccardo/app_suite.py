#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚽ FOOTBALL PREDICTION SUITE - APPLICATION PRINCIPALE
Application multi-pages avec fonctionnalités avancées

Pages disponibles:
1. 🏠 Accueil - Dashboard principal
2. 🔮 Prédictions Pro - Prédictions avancées
3. 📊 Analytics - Analyse comparative
4. 📈 Performances - Évaluation des modèles
5. ⚙️ Configuration - Paramètres avancés
"""

import streamlit as st
import sys
import os

# Configuration de la page
st.set_page_config(
    page_title="⚽ Football Prediction Suite", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS global amélioré
st.markdown("""
<style>
    /* Variables CSS */
    :root {
        --primary-color: #1e3c72;
        --secondary-color: #2a5298;
        --accent-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #f44336;
        --success-color: #4CAF50;
    }
    
    /* Header principal */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    /* Cards avec gradient */
    .gradient-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .gradient-card:hover {
        transform: translateY(-5px);
    }
    
    /* Navigation */
    .nav-item {
        padding: 0.8rem 1.5rem;
        margin: 0.2rem 0;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        border-left: 4px solid transparent;
    }
    
    .nav-item:hover {
        background-color: rgba(78, 121, 167, 0.1);
        border-left: 4px solid var(--accent-color);
    }
    
    .nav-item.active {
        background-color: rgba(78, 121, 167, 0.2);
        border-left: 4px solid var(--accent-color);
        font-weight: bold;
    }
    
    /* Métriques colorées */
    .metric-high { 
        color: var(--success-color); 
        font-weight: bold; 
        font-size: 1.2rem;
    }
    
    .metric-medium { 
        color: var(--warning-color); 
        font-weight: bold; 
        font-size: 1.2rem;
    }
    
    .metric-low { 
        color: var(--danger-color); 
        font-weight: bold; 
        font-size: 1.2rem;
    }
    
    /* Boutons stylisés */
    .stButton > button {
        background: linear-gradient(45deg, var(--accent-color), #45a049);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
    }
    
    /* Sidebar améliorée */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Prédiction card */
    .prediction-result {
        border: 3px solid var(--accent-color);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .score-display {
        font-size: 4rem;
        font-weight: bold;
        color: var(--primary-color);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Animation pour les éléments importants */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* Tables stylisées */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .score-display {
            font-size: 2.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_data_safe():
    """Charger les données de manière sécurisée"""
    try:
        import pandas as pd
        data = pd.read_csv('dataset.csv')
        data['Date'] = pd.to_datetime(data['Date'], format='mixed', dayfirst=True)
        data['Season'] = data['Date'].apply(
            lambda x: f"{x.year}-{str(x.year+1)[2:]}" if x.month >= 7 else f"{x.year-1}-{str(x.year)[2:]}"
        )
        return data
    except Exception as e:
        st.error(f"❌ Erreur de chargement des données: {str(e)}")
        return None

def show_home_page():
    """Page d'accueil avec dashboard principal"""
    st.markdown('<h1 class="main-header">⚽ Football Prediction Suite</h1>', unsafe_allow_html=True)
    
    # Chargement des données
    data = load_data_safe()
    if data is None:
        st.stop()
    
    # Statistiques générales
    st.subheader("📊 Vue d'ensemble des données")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_matches = len(data)
        st.markdown(f"""
        <div class="gradient-card">
            <h3>📈 Total Matchs</h3>
            <h2>{total_matches:,}</h2>
            <p>Données historiques</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_teams = len(set(list(data['HomeTeam'].unique()) + list(data['AwayTeam'].unique())))
        st.markdown(f"""
        <div class="gradient-card">
            <h3>🏆 Équipes</h3>
            <h2>{total_teams}</h2>
            <p>Championnat belge</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_seasons = len(data['Season'].unique())
        st.markdown(f"""
        <div class="gradient-card">
            <h3>📅 Saisons</h3>
            <h2>{total_seasons}</h2>
            <p>Historique complet</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_goals = (data['FTHG'].mean() + data['FTAG'].mean())
        st.markdown(f"""
        <div class="gradient-card">
            <h3>⚽ Moy. Buts</h3>
            <h2>{avg_goals:.1f}</h2>
            <p>Par match</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques de tendances
    st.subheader("📈 Tendances par saison")
    
    try:
        import plotly.express as px
        
        # Évolution des buts par saison
        season_stats = data.groupby('Season').agg({
            'FTHG': 'mean',
            'FTAG': 'mean',
            'Date': 'count'
        }).reset_index()
        
        season_stats['Total_Goals'] = season_stats['FTHG'] + season_stats['FTAG']
        season_stats = season_stats.rename(columns={'Date': 'Matches'})
        
        fig_goals = px.line(season_stats, x='Season', y='Total_Goals', 
                           title="⚽ Évolution des buts par saison",
                           markers=True)
        fig_goals.update_layout(
            xaxis_title="Saison",
            yaxis_title="Buts moyens par match"
        )
        
        st.plotly_chart(fig_goals, use_container_width=True)
        
    except ImportError:
        st.info("📊 Graphiques interactifs disponibles avec Plotly installé")
    
    # Guide de navigation
    st.subheader("🧭 Guide de Navigation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔮 Prédictions Pro
        - Prédictions avancées avec système de confiance
        - Analyse de forme récente des équipes
        - Modèles d'IA optimisés
        
        ### 📊 Analytics
        - Comparaison détaillée entre équipes
        - Analyse radar multi-critères
        - Confrontations directes
        """)
    
    with col2:
        st.markdown("""
        ### 📈 Performances
        - Évaluation des modèles de prédiction
        - Métriques de précision
        - Backtesting historique
        
        ### ⚙️ Configuration
        - Paramètres avancés
        - Sélection des modèles
        - Options d'export
        """)

def main():
    """Application principale avec navigation"""
    
    # Sidebar pour la navigation
    st.sidebar.title("🧭 Navigation")
    
    # Menu de navigation
    pages = {
        "🏠 Accueil": "home",
        "🔮 Prédictions Pro": "predictions", 
        "📊 Analytics": "analytics",
        "📈 Performances": "performance",
        "⚙️ Configuration": "config"
    }
    
    # Sélection de page
    selected_page = st.sidebar.radio(
        "Choisir une page :",
        list(pages.keys()),
        index=0
    )
    
    # Informations dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Informations")
    st.sidebar.info("""
    **Version:** 2.0 Pro  
    **Auteur:** Riccardo  
    **Mise à jour:** Janvier 2025
    
    🆕 Nouvelles fonctionnalités:
    - Dashboard interactif
    - Prédictions avec confiance
    - Analytics avancés
    - Graphiques Plotly
    """)
    
    # Navigation vers les pages
    page_code = pages[selected_page]
    
    if page_code == "home":
        show_home_page()
    
    elif page_code == "predictions":
        try:
            # Importer et exécuter le module de prédictions pro
            exec(open('Riccardo/football_prediction_pro.py').read())
        except FileNotFoundError:
            st.error("❌ Module de prédictions non trouvé")
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement: {str(e)}")
    
    elif page_code == "analytics":
        try:
            # Importer et exécuter le module d'analytics
            exec(open('Riccardo/analytics_advanced.py').read())
        except FileNotFoundError:
            st.error("❌ Module d'analytics non trouvé")
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement: {str(e)}")
    
    elif page_code == "performance":
        st.title("📈 Évaluation des Performances")
        st.info("🚧 Module en cours de développement")
        
        # Aperçu des fonctionnalités à venir
        st.markdown("""
        ### 🎯 Fonctionnalités prévues:
        
        - **Backtesting automatique** sur plusieurs saisons
        - **Métriques de performance** détaillées (R², MAE, RMSE)
        - **Comparaison de modèles** (RF, XGBoost, Ensemble)
        - **Analyse de la précision** par type de match
        - **Courbes ROC** pour les prédictions de résultat
        - **Profit/Loss simulation** pour les paris
        """)
    
    elif page_code == "config":
        st.title("⚙️ Configuration Avancée")
        
        st.subheader("🤖 Paramètres des Modèles")
        
        # Configuration des modèles
        model_type = st.selectbox(
            "Type de modèle principal:",
            ["Random Forest", "Gradient Boosting", "XGBoost", "Ensemble"]
        )
        
        confidence_threshold = st.slider(
            "Seuil de confiance minimum (%)",
            min_value=0,
            max_value=100,
            value=50,
            help="Prédictions en dessous de ce seuil seront marquées comme peu fiables"
        )
        
        st.subheader("📊 Paramètres d'Affichage")
        
        show_advanced_metrics = st.checkbox("Afficher les métriques avancées", value=True)
        show_confidence_intervals = st.checkbox("Afficher les intervalles de confiance", value=False)
        enable_notifications = st.checkbox("Activer les notifications", value=True)
        
        # Sauvegarde des paramètres (simulation)
        if st.button("💾 Sauvegarder la Configuration"):
            st.success("✅ Configuration sauvegardée avec succès!")
            st.balloons()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        ⚽ Football Prediction Suite v2.0 | Développé avec ❤️ par Riccardo | 
        <a href='https://github.com/becodeorg/football-prediction-liverpool' target='_blank'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
