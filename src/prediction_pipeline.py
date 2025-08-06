"""
Pipeline de prédiction pour les matchs de football
Utilise le modèle Gradient Boosting optimisé pour prédire les résultats de matchs

Version: 2.0 - Optimisé avec les meilleures performances (51% accuracy)
Auteur: Data Science Team
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import des fonctions de preprocessing existantes
try:
    from preprocessing import (
        clean_data, 
        get_team_history, 
        calculate_form, 
        create_team_features, 
        add_additional_features, 
        validate_and_clean_features
    )
    PREPROCESSING_AVAILABLE = True
    print("✅ Fonctions de preprocessing importées")
except ImportError:
    print("⚠️ Impossible d'importer les fonctions de preprocessing")
    PREPROCESSING_AVAILABLE = False

class FootballPredictor:
    """
    Classe principale pour la prédiction de matchs de football
    
    Utilise le modèle Gradient Boosting pré-entraîné et les fonctions
    de feature engineering pour prédire le résultat d'un match.
    """
    
    def __init__(self, model_path=None, data_path=None):
        """
        Initialise le prédicteur avec le modèle et les données
        
        Args:
            model_path (str): Chemin vers le modèle sauvegardé
            data_path (str): Chemin vers le dataset pour l'historique
        """
        # Déterminer le répertoire racine du projet
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Chemins par défaut
        if model_path is None:
            model_path = project_root / "models" / "gb_model.pkl"
        if data_path is None:
            # Utiliser le dataset preprocessé (compatible avec le modèle entraîné)
            data_path = project_root / "data" / "processed" / "data_2023_2026_final.csv"
            
        self.model_path = Path(model_path)
        self.data_path = Path(data_path)
        self.model = None
        self.scaler = None
        self.historical_data = None
        self.feature_columns = None
        
        # Charger les composants
        self._load_model()
        self._load_data()
        
    def _load_model(self):
        """Charge le modèle et le scaler"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                print(f"✅ Modèle chargé depuis {self.model_path}")
            else:
                raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")
                
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            raise
    
    def _load_data(self):
        """Charge les données historiques pour le feature engineering"""
        try:
            if self.data_path.exists():
                self.historical_data = pd.read_csv(self.data_path)
                self.historical_data['Date'] = pd.to_datetime(self.historical_data['Date'])
                self.historical_data = self.historical_data.sort_values('Date')
                
                # Identifier les colonnes de features
                exclude_cols = ['Date', 'HomeTeam', 'AwayTeam', 'Target', 'Target_encoded']
                self.feature_columns = [col for col in self.historical_data.columns 
                                      if col not in exclude_cols]
                
                print(f"✅ Données historiques chargées: {len(self.historical_data)} matchs")
                print(f"📊 Features disponibles: {len(self.feature_columns)}")
            else:
                raise FileNotFoundError(f"Dataset non trouvé: {self.data_path}")
                
        except Exception as e:
            print(f"❌ Erreur lors du chargement des données: {e}")
            raise
    
    def get_team_list(self):
        """
        Retourne la liste des équipes disponibles dans les données
        
        Returns:
            list: Liste des noms d'équipes
        """
        if self.historical_data is not None:
            home_teams = set(self.historical_data['HomeTeam'].unique())
            away_teams = set(self.historical_data['AwayTeam'].unique())
            return sorted(list(home_teams.union(away_teams)))
        return []
    
    def predict_match(self, home_team, away_team, use_latest_data=True):
        """
        Prédit le résultat d'un match entre deux équipes
        
        Args:
            home_team (str): Nom de l'équipe à domicile
            away_team (str): Nom de l'équipe à l'extérieur
            use_latest_data (bool): Utiliser les données les plus récentes
            
        Returns:
            dict: Prédictions avec probabilités et métadonnées
        """
        if self.model is None or self.historical_data is None:
            raise ValueError("Modèle ou données non chargés")
        
        try:
            # Vérifier que les équipes existent
            available_teams = self.get_team_list()
            if home_team not in available_teams:
                raise ValueError(f"Équipe domicile '{home_team}' non trouvée dans les données")
            if away_team not in available_teams:
                raise ValueError(f"Équipe extérieure '{away_team}' non trouvée dans les données")
            
            # Créer un match fictif pour le feature engineering
            # Version 2: Utilise les fonctions de preprocessing existantes
            match_features = self._create_match_features_v2(home_team, away_team)
            
            # Préparer les features pour la prédiction
            feature_vector = self._prepare_features(match_features)
            
            # Prédiction
            probabilities = self.model.predict_proba([feature_vector])[0]
            
            # Formater les résultats
            result = {
                'teams': {
                    'home': home_team,
                    'away': away_team
                },
                'predictions': {
                    'home_win': float(probabilities[0]),
                    'draw': float(probabilities[1]),
                    'away_win': float(probabilities[2])
                },
                'confidence': float(max(probabilities)),
                'most_likely': self._get_most_likely_outcome(probabilities),
                'features_used': len(self.feature_columns)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur lors de la prédiction: {e}")
            return {
                'error': str(e),
                'teams': {'home': home_team, 'away': away_team}
            }
    
    def _create_match_features_v2(self, home_team, away_team, n_matches=5):
        """
        Version alternative utilisant les fonctions de preprocessing existantes
        
        Args:
            home_team (str): Équipe domicile
            away_team (str): Équipe extérieure
            n_matches (int): Nombre de matchs d'historique à considérer
            
        Returns:
            dict: Features calculées pour le match
        """
        # TEMPORAIRE: Dataset déjà preprocessé, pas besoin des fonctions de preprocessing
        print("ℹ️ Dataset déjà preprocessé, utilisation de la méthode manuelle")
        return self._create_match_features(home_team, away_team, n_matches)
        
        # CODE ORIGINAL COMMENTÉ (pour référence future)
        # if not PREPROCESSING_AVAILABLE:
        #     return self._create_match_features(home_team, away_team, n_matches)
        # 
        # try:
        #     # Ce code fonctionne seulement avec des données brutes non-preprocessées
        #     latest_date = self.historical_data['Date'].max()
        #     future_date = latest_date + pd.Timedelta(days=1)
        #     
        #     future_match = pd.DataFrame({
        #         'Date': [future_date],
        #         'HomeTeam': [home_team],
        #         'AwayTeam': [away_team],
        #         'Target': ['H']
        #     })
        #     
        #     temp_df = pd.concat([self.historical_data, future_match], ignore_index=True)
        #     features_df = create_team_features(temp_df, n_matches)
        #     last_row = features_df.iloc[-1]
        #     
        #     features = {}
        #     for col in self.feature_columns:
        #         if col in last_row.index:
        #             features[col] = last_row[col]
        #         else:
        #             features[col] = 0
        #             
        #     return features
        #     
        # except Exception as e:
        #     print(f"⚠️ Erreur avec preprocessing existant: {e}")
        #     return self._create_match_features(home_team, away_team, n_matches)
    
    def _create_match_features(self, home_team, away_team, n_matches=5):
        """
        Crée les features pour un match à partir de l'historique des équipes
        
        Args:
            home_team (str): Équipe domicile
            away_team (str): Équipe extérieure
            n_matches (int): Nombre de matchs d'historique à considérer
            
        Returns:
            dict: Features calculées pour le match
        """
        # Utiliser la date la plus récente + 1 jour pour simuler un match futur
        latest_date = self.historical_data['Date'].max()
        match_date = latest_date + pd.Timedelta(days=1)
        
        # Simuler un match pour le feature engineering
        fake_match = {
            'Date': match_date,
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            'Target': 'H'  # Valeur temporaire
        }
        
        # Calculer les features moyennes pour chaque équipe
        home_features = self._get_team_recent_stats(home_team, n_matches)
        away_features = self._get_team_recent_stats(away_team, n_matches)
        
        # Créer le vecteur de features
        features = {}
        
        # Features domicile
        features['home_avg_goals_scored'] = home_features.get('avg_goals_scored', 0)
        features['home_avg_goals_conceded'] = home_features.get('avg_goals_conceded', 0)
        features['home_avg_shots'] = home_features.get('avg_shots', 0)
        features['home_avg_shots_target'] = home_features.get('avg_shots_target', 0)
        features['home_avg_corners'] = home_features.get('avg_corners', 0)
        features['home_win_rate'] = home_features.get('win_rate', 0)
        features['home_form'] = home_features.get('form', 0)
        
        # Features extérieur
        features['away_avg_goals_scored'] = away_features.get('avg_goals_scored', 0)
        features['away_avg_goals_conceded'] = away_features.get('avg_goals_conceded', 0)
        features['away_avg_shots'] = away_features.get('avg_shots', 0)
        features['away_avg_shots_target'] = away_features.get('avg_shots_target', 0)
        features['away_avg_corners'] = away_features.get('avg_corners', 0)
        features['away_win_rate'] = away_features.get('win_rate', 0)
        features['away_form'] = away_features.get('form', 0)
        
        # Features dérivées optimisées (basées sur l'analyse neural network)
        features['goal_difference'] = features['home_avg_goals_scored'] - features['away_avg_goals_scored']
        features['form_difference'] = features['home_form'] - features['away_form']
        features['home_shot_efficiency'] = (features['home_avg_shots_target'] / features['home_avg_shots'] 
                                          if features['home_avg_shots'] > 0 else 0)
        features['away_shot_efficiency'] = (features['away_avg_shots_target'] / features['away_avg_shots'] 
                                          if features['away_avg_shots'] > 0 else 0)
        
        # Features additionnelles optimisées (issues du feature engineering neural network)
        features['home_advantage'] = features['home_win_rate'] - features['away_win_rate']
        features['goal_efficiency_gap'] = (
            features['home_shot_efficiency'] * features['home_avg_goals_scored'] - 
            features['away_shot_efficiency'] * features['away_avg_goals_scored']
        )
        features['defensive_strength_ratio'] = (
            features['away_avg_goals_conceded'] / (features['home_avg_goals_conceded'] + 0.01)
        )
        
        return features
    
    def _get_team_recent_stats(self, team, n_matches=5):
        """
        Calcule les statistiques récentes d'une équipe
        
        Args:
            team (str): Nom de l'équipe
            n_matches (int): Nombre de matchs à considérer
            
        Returns:
            dict: Statistiques moyennes de l'équipe
        """
        # Matchs récents de l'équipe (domicile et extérieur)
        team_matches = self.historical_data[
            (self.historical_data['HomeTeam'] == team) | 
            (self.historical_data['AwayTeam'] == team)
        ].tail(n_matches)
        
        if len(team_matches) == 0:
            return {
                'avg_goals_scored': 0,
                'avg_goals_conceded': 0,
                'avg_shots': 0,
                'avg_shots_target': 0,
                'avg_corners': 0,
                'win_rate': 0,
                'form': 0
            }
        
        stats = {
            'goals_scored': [],
            'goals_conceded': [],
            'shots': [],
            'shots_target': [],
            'corners': [],
            'results': []
        }
        
        for _, match in team_matches.iterrows():
            if match['HomeTeam'] == team:
                # Équipe joue à domicile
                stats['goals_scored'].append(match.get('home_goals', 0))
                stats['goals_conceded'].append(match.get('away_goals', 0))
                stats['shots'].append(match.get('home_shots', 0))
                stats['shots_target'].append(match.get('home_shots_target', 0))
                stats['corners'].append(match.get('home_corners', 0))
                stats['results'].append('W' if match.get('Target') == 'H' else 
                                      'D' if match.get('Target') == 'D' else 'L')
            else:
                # Équipe joue à l'extérieur
                stats['goals_scored'].append(match.get('away_goals', 0))
                stats['goals_conceded'].append(match.get('home_goals', 0))
                stats['shots'].append(match.get('away_shots', 0))
                stats['shots_target'].append(match.get('away_shots_target', 0))
                stats['corners'].append(match.get('away_corners', 0))
                stats['results'].append('W' if match.get('Target') == 'A' else 
                                      'D' if match.get('Target') == 'D' else 'L')
        
        # Calculer les moyennes
        return {
            'avg_goals_scored': np.mean(stats['goals_scored']) if stats['goals_scored'] else 0,
            'avg_goals_conceded': np.mean(stats['goals_conceded']) if stats['goals_conceded'] else 0,
            'avg_shots': np.mean(stats['shots']) if stats['shots'] else 0,
            'avg_shots_target': np.mean(stats['shots_target']) if stats['shots_target'] else 0,
            'avg_corners': np.mean(stats['corners']) if stats['corners'] else 0,
            'win_rate': sum(1 for r in stats['results'] if r == 'W') / len(stats['results']) if stats['results'] else 0,
            'form': self._calculate_team_form(stats['results'])
        }
    
    def _calculate_team_form(self, results):
        """
        Calcule la forme d'une équipe basée sur les résultats récents
        
        Args:
            results (list): Liste des résultats ('W', 'D', 'L')
            
        Returns:
            float: Forme de l'équipe (points par match)
        """
        if not results:
            return 0
        
        points = [3 if r == 'W' else 1 if r == 'D' else 0 for r in results]
        return sum(points) / len(points)
    
    def _prepare_features(self, features_dict):
        """
        Prépare le vecteur de features pour la prédiction
        
        Args:
            features_dict (dict): Dictionnaire des features
            
        Returns:
            list: Vecteur de features ordonné
        """
        # Créer un vecteur avec toutes les features dans le bon ordre
        feature_vector = []
        
        for col in self.feature_columns:
            value = features_dict.get(col, 0)
            feature_vector.append(value)
        
        # Appliquer la normalisation si disponible
        if self.scaler is not None:
            feature_vector = self.scaler.transform([feature_vector])[0]
        
        return feature_vector
    
    def _get_most_likely_outcome(self, probabilities):
        """
        Détermine le résultat le plus probable
        
        Args:
            probabilities (array): Probabilités [home, draw, away]
            
        Returns:
            str: Résultat le plus probable
        """
        outcomes = ['home_win', 'draw', 'away_win']
        max_idx = np.argmax(probabilities)
        return outcomes[max_idx]
    
    def predict_multiple_matches(self, matches):
        """
        Prédit plusieurs matchs en une fois
        
        Args:
            matches (list): Liste de tuples (home_team, away_team)
            
        Returns:
            list: Liste des prédictions
        """
        results = []
        for home_team, away_team in matches:
            prediction = self.predict_match(home_team, away_team)
            results.append(prediction)
        return results
    
    def get_model_info(self):
        """
        Retourne des informations sur le modèle
        
        Returns:
            dict: Informations sur le modèle
        """
        return {
            'model_type': type(self.model).__name__,
            'feature_count': len(self.feature_columns) if self.feature_columns else 0,
            'data_size': len(self.historical_data) if self.historical_data is not None else 0,
            'teams_available': len(self.get_team_list()),
            'has_scaler': self.scaler is not None
        }


# Fonction utilitaire pour un test rapide
def test_prediction():
    """Test simple du pipeline"""
    try:
        predictor = FootballPredictor()
        teams = predictor.get_team_list()
        
        if len(teams) >= 2:
            result = predictor.predict_match(teams[0], teams[1])
            print("🧪 Test de prédiction:")
            print(f"Match: {teams[0]} vs {teams[1]}")
            print(f"Résultat: {result}")
            
            # Test avec plusieurs équipes populaires
            print(f"\n🎯 Tests supplémentaires:")
            popular_teams = ['Anderlecht', 'Club Brugge', 'Genk', 'Standard']
            available_popular = [t for t in popular_teams if t in teams]
            
            if len(available_popular) >= 2:
                for i in range(min(3, len(available_popular)-1)):
                    home = available_popular[i]
                    away = available_popular[i+1]
                    result = predictor.predict_match(home, away)
                    probs = result['predictions']
                    
                    print(f"  {home} vs {away}:")
                    print(f"    Victoire {home}: {probs['home_win']:.1%}")
                    print(f"    Match nul: {probs['draw']:.1%}")
                    print(f"    Victoire {away}: {probs['away_win']:.1%}")
                    print(f"    Prédiction: {result['most_likely']}")
                    print(f"    Confiance: {result['confidence']:.1%}")
            
            print(f"\n📊 Informations du modèle:")
            info = predictor.get_model_info()
            for key, value in info.items():
                print(f"  {key}: {value}")
                
            return True
        else:
            print("❌ Pas assez d'équipes dans les données")
            return False
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Pipeline de prédiction Football")
    print("=" * 50)
    
    # Test du pipeline
    test_prediction()
