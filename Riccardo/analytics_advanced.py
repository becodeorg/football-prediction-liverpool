#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 SYSTÈME D'ANALYSE COMPARATIVE FOOTBALL
Module d'analyse avancée pour comparer les équipes et évaluer les prédictions

Fonctionnalités:
- Analyse head-to-head détaillée
- Comparaison statistique multi-critères 
- Système de scoring avancé
- Visualisations interactives
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

class FootballAnalytics:
    """Classe pour l'analyse avancée des données football"""
    
    def __init__(self, data):
        self.data = data
        self.teams = sorted(set(list(data['HomeTeam'].unique()) + list(data['AwayTeam'].unique())))
    
    def get_head_to_head(self, team1, team2, last_n_matches=10):
        """Analyser les confrontations directes entre deux équipes"""
        h2h_matches = self.data[
            ((self.data['HomeTeam'] == team1) & (self.data['AwayTeam'] == team2)) |
            ((self.data['HomeTeam'] == team2) & (self.data['AwayTeam'] == team1))
        ].sort_values('Date', ascending=False).head(last_n_matches)
        
        if len(h2h_matches) == 0:
            return None
        
        # Statistiques pour team1
        team1_wins = 0
        team2_wins = 0
        draws = 0
        team1_goals = 0
        team2_goals = 0
        
        for _, match in h2h_matches.iterrows():
            if match['HomeTeam'] == team1:
                team1_goals += match['FTHG']
                team2_goals += match['FTAG']
                if match['FTR'] == 'H':
                    team1_wins += 1
                elif match['FTR'] == 'D':
                    draws += 1
                else:
                    team2_wins += 1
            else:
                team1_goals += match['FTAG']
                team2_goals += match['FTHG']
                if match['FTR'] == 'A':
                    team1_wins += 1
                elif match['FTR'] == 'D':
                    draws += 1
                else:
                    team2_wins += 1
        
        return {
            'matches': h2h_matches,
            'total_matches': len(h2h_matches),
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_goals': team1_goals,
            'team2_goals': team2_goals,
            'avg_goals_team1': team1_goals / len(h2h_matches),
            'avg_goals_team2': team2_goals / len(h2h_matches)
        }
    
    def calculate_team_power_rating(self, team_name, seasons=None):
        """Calculer un rating de puissance pour une équipe"""
        if seasons:
            team_data = self.data[self.data['Season'].isin(seasons)]
        else:
            team_data = self.data
        
        # Matchs à domicile
        home_matches = team_data[team_data['HomeTeam'] == team_name]
        # Matchs à l'extérieur
        away_matches = team_data[team_data['AwayTeam'] == team_name]
        
        if len(home_matches) + len(away_matches) == 0:
            return 0
        
        # Calcul des métriques
        total_matches = len(home_matches) + len(away_matches)
        
        # Points (3 victoire, 1 nul, 0 défaite)
        home_points = len(home_matches[home_matches['FTR'] == 'H']) * 3 + len(home_matches[home_matches['FTR'] == 'D'])
        away_points = len(away_matches[away_matches['FTR'] == 'A']) * 3 + len(away_matches[away_matches['FTR'] == 'D'])
        total_points = home_points + away_points
        
        # Buts
        goals_scored = home_matches['FTHG'].sum() + away_matches['FTAG'].sum()
        goals_conceded = home_matches['FTAG'].sum() + away_matches['FTHG'].sum()
        
        # Tirs et efficacité
        avg_shots_on_target = (home_matches['HST'].mean() + away_matches['AST'].mean()) / 2
        avg_shots = (home_matches['HS'].mean() + away_matches['AS'].mean()) / 2
        
        # Rating composite (0-100)
        points_per_match = total_points / total_matches if total_matches > 0 else 0
        goal_difference_per_match = (goals_scored - goals_conceded) / total_matches if total_matches > 0 else 0
        
        # Normalisation et pondération
        power_rating = (
            (points_per_match / 3) * 40 +  # 40% basé sur les points
            ((goal_difference_per_match + 2) / 4) * 30 +  # 30% différence de buts (normalisé)
            (avg_shots_on_target / 10) * 20 +  # 20% efficacité offensive
            (min(avg_shots / 15, 1)) * 10  # 10% volume de jeu
        ) * 100
        
        return min(100, max(0, power_rating))
    
    def create_radar_chart(self, team1, team2, seasons=None):
        """Créer un graphique radar comparatif"""
        if seasons:
            data_filtered = self.data[self.data['Season'].isin(seasons)]
        else:
            data_filtered = self.data
        
        metrics = []
        team1_values = []
        team2_values = []
        
        # Collecte des métriques
        for team, values in [(team1, team1_values), (team2, team2_values)]:
            home_matches = data_filtered[data_filtered['HomeTeam'] == team]
            away_matches = data_filtered[data_filtered['AwayTeam'] == team]
            
            if len(home_matches) + len(away_matches) == 0:
                values.extend([0] * 8)
                continue
            
            # Calculs des métriques
            total_matches = len(home_matches) + len(away_matches)
            
            # 1. Points par match
            home_points = len(home_matches[home_matches['FTR'] == 'H']) * 3 + len(home_matches[home_matches['FTR'] == 'D'])
            away_points = len(away_matches[away_matches['FTR'] == 'A']) * 3 + len(away_matches[away_matches['FTR'] == 'D'])
            points_per_match = (home_points + away_points) / total_matches if total_matches > 0 else 0
            
            # 2. Buts marqués par match
            goals_scored = home_matches['FTHG'].sum() + away_matches['FTAG'].sum()
            goals_per_match = goals_scored / total_matches if total_matches > 0 else 0
            
            # 3. Buts encaissés par match (inversé pour le radar)
            goals_conceded = home_matches['FTAG'].sum() + away_matches['FTHG'].sum()
            defense_rating = max(0, 3 - (goals_conceded / total_matches)) if total_matches > 0 else 0
            
            # 4. Tirs cadrés par match
            shots_on_target = (home_matches['HST'].mean() + away_matches['AST'].mean()) / 2
            shots_on_target = shots_on_target if not pd.isna(shots_on_target) else 0
            
            # 5. Efficacité (buts/tirs cadrés)
            efficiency = (goals_scored / (shots_on_target * total_matches)) * 100 if shots_on_target > 0 else 0
            efficiency = min(efficiency, 50)  # Plafonner à 50%
            
            # 6. Domination domicile
            home_win_rate = len(home_matches[home_matches['FTR'] == 'H']) / len(home_matches) * 100 if len(home_matches) > 0 else 0
            
            # 7. Performance extérieur
            away_win_rate = len(away_matches[away_matches['FTR'] == 'A']) / len(away_matches) * 100 if len(away_matches) > 0 else 0
            
            # 8. Régularité (basée sur l'écart-type des buts)
            all_goals = list(home_matches['FTHG']) + list(away_matches['FTAG'])
            consistency = max(0, 100 - np.std(all_goals) * 20) if len(all_goals) > 0 else 0
            
            values.extend([
                points_per_match,
                goals_per_match,
                defense_rating,
                shots_on_target / 2,  # Normaliser
                efficiency,
                home_win_rate / 20,  # Normaliser
                away_win_rate / 20,  # Normaliser
                consistency / 20  # Normaliser
            ])
        
        # Définir les métriques une seule fois
        if not metrics:
            metrics = [
                'Points/Match',
                'Buts/Match',
                'Solidité Défensive',
                'Tirs Cadrés',
                'Efficacité',
                'Force Domicile',
                'Performance Ext.',
                'Régularité'
            ]
        
        # Créer le graphique radar
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=team1_values + [team1_values[0]],  # Fermer le polygone
            theta=metrics + [metrics[0]],
            fill='toself',
            name=team1,
            line_color='rgba(0, 100, 200, 0.8)',
            fillcolor='rgba(0, 100, 200, 0.2)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=team2_values + [team2_values[0]],  # Fermer le polygone
            theta=metrics + [metrics[0]],
            fill='toself',
            name=team2,
            line_color='rgba(200, 50, 50, 0.8)',
            fillcolor='rgba(200, 50, 50, 0.2)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            title="📊 Comparaison Radar des Équipes"
        )
        
        return fig

def show_analytics_dashboard():
    """Afficher le dashboard d'analyse avancée"""
    st.title("📊 Analyse Comparative Avancée")
    
    # Charger les données
    @st.cache_data
    def load_data():
        try:
            data = pd.read_csv('dataset.csv')
            data['Date'] = pd.to_datetime(data['Date'], format='mixed', dayfirst=True)
            # Ajouter la saison
            data['Season'] = data['Date'].apply(lambda x: f"{x.year}-{str(x.year+1)[2:]}" if x.month >= 7 else f"{x.year-1}-{str(x.year)[2:]}")
            return data
        except:
            return None
    
    data = load_data()
    if data is None:
        st.error("❌ Impossible de charger les données")
        return
    
    # Initialiser l'analyseur
    analytics = FootballAnalytics(data)
    
    # Interface utilisateur
    col1, col2 = st.columns(2)
    
    with col1:
        team1 = st.selectbox("🏠 Première équipe:", analytics.teams, index=0)
    
    with col2:
        team2 = st.selectbox("✈️ Deuxième équipe:", analytics.teams, 
                            index=1 if len(analytics.teams) > 1 else 0)
    
    if team1 == team2:
        st.warning("⚠️ Veuillez sélectionner deux équipes différentes")
        return
    
    # Sélection des saisons
    available_seasons = sorted(data['Season'].unique())
    selected_seasons = st.multiselect(
        "📅 Saisons à analyser:",
        options=available_seasons,
        default=available_seasons[-2:],
        help="Choisissez les saisons pour l'analyse"
    )
    
    if not selected_seasons:
        st.warning("⚠️ Veuillez sélectionner au moins une saison")
        return
    
    # Analyse Head-to-Head
    st.subheader("⚔️ Confrontations Directes")
    h2h = analytics.get_head_to_head(team1, team2)
    
    if h2h:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏆 Victoires " + team1, h2h['team1_wins'])
        
        with col2:
            st.metric("🏆 Victoires " + team2, h2h['team2_wins'])
        
        with col3:
            st.metric("🤝 Matchs Nuls", h2h['draws'])
        
        with col4:
            st.metric("📊 Total Matchs", h2h['total_matches'])
        
        # Graphique des buts en confrontation directe
        goals_data = pd.DataFrame({
            'Équipe': [team1, team2],
            'Buts Totaux': [h2h['team1_goals'], h2h['team2_goals']],
            'Moyenne': [h2h['avg_goals_team1'], h2h['avg_goals_team2']]
        })
        
        fig_h2h = px.bar(goals_data, x='Équipe', y='Buts Totaux', 
                        title="⚽ Buts en Confrontations Directes",
                        color='Équipe')
        st.plotly_chart(fig_h2h, use_container_width=True)
    else:
        st.info("ℹ️ Aucune confrontation directe trouvée dans les données")
    
    # Power Ratings
    st.subheader("⚡ Power Ratings")
    
    team1_rating = analytics.calculate_team_power_rating(team1, selected_seasons)
    team2_rating = analytics.calculate_team_power_rating(team2, selected_seasons)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🔥 Rating " + team1, f"{team1_rating:.1f}/100")
        
    with col2:
        st.metric("🔥 Rating " + team2, f"{team2_rating:.1f}/100")
    
    # Graphique radar comparatif
    st.subheader("📊 Analyse Radar Comparative")
    radar_chart = analytics.create_radar_chart(team1, team2, selected_seasons)
    st.plotly_chart(radar_chart, use_container_width=True)
    
    # Analyse détaillée des statistiques
    st.subheader("📈 Statistiques Détaillées")
    
    # Préparer les données pour les deux équipes
    team_stats = {}
    
    for team in [team1, team2]:
        data_filtered = data[data['Season'].isin(selected_seasons)]
        home_matches = data_filtered[data_filtered['HomeTeam'] == team]
        away_matches = data_filtered[data_filtered['AwayTeam'] == team]
        
        if len(home_matches) + len(away_matches) > 0:
            total_matches = len(home_matches) + len(away_matches)
            
            # Victoires, nuls, défaites
            home_wins = len(home_matches[home_matches['FTR'] == 'H'])
            away_wins = len(away_matches[away_matches['FTR'] == 'A'])
            draws = len(home_matches[home_matches['FTR'] == 'D']) + len(away_matches[away_matches['FTR'] == 'D'])
            losses = total_matches - (home_wins + away_wins + draws)
            
            # Buts
            goals_scored = home_matches['FTHG'].sum() + away_matches['FTAG'].sum()
            goals_conceded = home_matches['FTAG'].sum() + away_matches['FTHG'].sum()
            
            team_stats[team] = {
                'Matchs Joués': total_matches,
                'Victoires': home_wins + away_wins,
                'Nuls': draws,
                'Défaites': losses,
                'Buts Marqués': goals_scored,
                'Buts Encaissés': goals_conceded,
                'Diff. de Buts': goals_scored - goals_conceded,
                'Points': (home_wins + away_wins) * 3 + draws,
                'Moy. Buts/Match': round(goals_scored / total_matches, 2) if total_matches > 0 else 0,
                'Moy. Encaissés/Match': round(goals_conceded / total_matches, 2) if total_matches > 0 else 0
            }
    
    # Afficher le tableau comparatif
    if team_stats:
        stats_df = pd.DataFrame(team_stats).T
        st.dataframe(stats_df, use_container_width=True)
        
        # Graphiques de comparaison
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique des buts marqués vs encaissés
            goals_comparison = pd.DataFrame({
                'Équipe': [team1, team2],
                'Buts Marqués': [team_stats[team1]['Buts Marqués'], team_stats[team2]['Buts Marqués']],
                'Buts Encaissés': [team_stats[team1]['Buts Encaissés'], team_stats[team2]['Buts Encaissés']]
            })
            
            fig_goals = px.bar(goals_comparison, x='Équipe', y=['Buts Marqués', 'Buts Encaissés'],
                             title="⚽ Comparaison Offensive/Défensive", barmode='group')
            st.plotly_chart(fig_goals, use_container_width=True)
        
        with col2:
            # Graphique en secteurs des résultats
            results_team1 = [team_stats[team1]['Victoires'], team_stats[team1]['Nuls'], team_stats[team1]['Défaites']]
            results_team2 = [team_stats[team2]['Victoires'], team_stats[team2]['Nuls'], team_stats[team2]['Défaites']]
            
            fig_results = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                      subplot_titles=[team1, team2])
            
            fig_results.add_trace(go.Pie(labels=['Victoires', 'Nuls', 'Défaites'], 
                                       values=results_team1, name=team1), 1, 1)
            fig_results.add_trace(go.Pie(labels=['Victoires', 'Nuls', 'Défaites'], 
                                       values=results_team2, name=team2), 1, 2)
            
            fig_results.update_traces(hole=.4, hoverinfo="label+percent+name")
            fig_results.update_layout(title_text="📊 Répartition des Résultats")
            
            st.plotly_chart(fig_results, use_container_width=True)

if __name__ == "__main__":
    show_analytics_dashboard()
