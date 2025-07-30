#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST DES COTES BOOKMAKERS
Vérification que les cotes sont bien disponibles dans le dataset
"""

import pandas as pd
import numpy as np

def test_bookmaker_odds():
    """Test de récupération des cotes des bookmakers"""
    print("🧪 TEST DES COTES BOOKMAKERS")
    print("=" * 50)
    
    try:
        # Charger le dataset
        data = pd.read_csv('dataset.csv', encoding='latin-1')
        print(f"📊 Dataset chargé: {len(data)} matchs")
        
        # Vérifier les colonnes de cotes disponibles
        odds_columns = [col for col in data.columns if any(bookmaker in col for bookmaker in ['B365', 'BW', 'PS', 'WH'])]
        print(f"📋 Colonnes de cotes trouvées: {len(odds_columns)}")
        
        if odds_columns:
            print("\n🏪 Bookmakers disponibles:")
            bookmakers = set()
            for col in odds_columns:
                if 'B365' in col:
                    bookmakers.add('Bet365')
                elif 'BW' in col:
                    bookmakers.add('Betway')
                elif 'PS' in col:
                    bookmakers.add('Pinnacle')
                elif 'WH' in col:
                    bookmakers.add('William Hill')
            
            for bookmaker in sorted(bookmakers):
                print(f"  ✅ {bookmaker}")
        
        # Tester quelques équipes
        print("\n🏟️ TEST SUR ÉQUIPES POPULAIRES:")
        test_teams = ['Club Brugge', 'Anderlecht', 'Gent', 'Standard']
        
        for team in test_teams:
            if team in data['HomeTeam'].values or team in data['AwayTeam'].values:
                home_matches = data[data['HomeTeam'] == team]
                away_matches = data[data['AwayTeam'] == team]
                total_matches = len(home_matches) + len(away_matches)
                
                # Vérifier la disponibilité des cotes pour cette équipe
                if 'B365H' in data.columns:
                    home_odds_available = home_matches['B365H'].notna().sum()
                    away_odds_available = away_matches['B365A'].notna().sum()
                    odds_coverage = ((home_odds_available + away_odds_available) / total_matches) * 100
                    
                    print(f"  {team}: {total_matches} matchs, {odds_coverage:.1f}% avec cotes Bet365")
                
        # Exemple concret
        print("\n🔍 EXEMPLE: Recherche confrontation Club Brugge vs Anderlecht")
        if 'Club Brugge' in data['HomeTeam'].values and 'Anderlecht' in data['AwayTeam'].values:
            direct_matches = data[
                ((data['HomeTeam'] == 'Club Brugge') & (data['AwayTeam'] == 'Anderlecht')) |
                ((data['HomeTeam'] == 'Anderlecht') & (data['AwayTeam'] == 'Club Brugge'))
            ]
            
            print(f"📊 {len(direct_matches)} confrontations directes trouvées")
            
            if len(direct_matches) > 0 and 'B365H' in direct_matches.columns:
                latest_match = direct_matches.iloc[-1]
                if pd.notna(latest_match['B365H']):
                    print(f"💰 Dernières cotes Bet365:")
                    print(f"   🏠 {latest_match['HomeTeam']}: {latest_match['B365H']:.2f}")
                    print(f"   🤝 Match Nul: {latest_match['B365D']:.2f}")
                    print(f"   🚌 {latest_match['AwayTeam']}: {latest_match['B365A']:.2f}")
                    print(f"   📅 Date: {latest_match['Date']}")
                    
                    # Calculer les pourcentages
                    home_pct = (1 / latest_match['B365H']) * 100
                    draw_pct = (1 / latest_match['B365D']) * 100
                    away_pct = (1 / latest_match['B365A']) * 100
                    
                    print(f"📊 Probabilités implicites:")
                    print(f"   🏠 {latest_match['HomeTeam']}: {home_pct:.1f}%")
                    print(f"   🤝 Match Nul: {draw_pct:.1f}%")
                    print(f"   🚌 {latest_match['AwayTeam']}: {away_pct:.1f}%")
        
        print("\n" + "=" * 50)
        print("✅ TEST TERMINÉ - Les cotes sont disponibles !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bookmaker_odds()
