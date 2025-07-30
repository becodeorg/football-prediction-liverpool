"""
Script principal pour le preprocessing des données de football
Usage: python main.py
"""

import sys
from pathlib import Path

# Ajouter le dossier src au path
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent / "config"))

import pandas as pd
from preprocessing import clean_data, create_team_features, add_additional_features, validate_and_clean_features
from config import RAW_DATASET, PROCESSED_DATASET

def main():
    """
    Pipeline principal de preprocessing
    """
    print("🏈 Football Prediction - Preprocessing Pipeline")
    print("=" * 50)
    
    # 1. Chargement des données
    print(f"📖 Chargement des données depuis: {RAW_DATASET}")
    if not RAW_DATASET.exists():
        print(f"❌ Erreur: Le fichier {RAW_DATASET} n'existe pas!")
        return
    
    df = pd.read_csv(RAW_DATASET)
    print(f"✅ Dataset chargé: {len(df)} lignes, {len(df.columns)} colonnes")
    
    # 2. Nettoyage initial
    print("\n🧹 Nettoyage des données...")
    df_clean = clean_data(df.copy())
    print(f"✅ Données nettoyées: {len(df_clean)} lignes restantes")
    
    # 3. Création des features d'historique
    print("\n🔧 Création des features d'historique des équipes...")
    df_features = create_team_features(df_clean, n_matches=5)
    print(f"✅ Features d'historique créées: {len(df_features)} matchs avec historique")
    
    # 4. Ajout de features dérivées
    print("\n➕ Ajout de features supplémentaires...")
    df_features = add_additional_features(df_features)
    print(f"✅ Features supplémentaires ajoutées")
    
    # 5. Validation et nettoyage final
    print("\n✨ Validation et nettoyage final...")
    df_final = validate_and_clean_features(df_features)
    print(f"✅ Dataset final: {len(df_final)} lignes, {len(df_final.columns)} colonnes")
    
    # 6. Sauvegarde
    print(f"\n💾 Sauvegarde du dataset final: {PROCESSED_DATASET}")
    PROCESSED_DATASET.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(PROCESSED_DATASET, index=False)
    print("✅ Dataset sauvegardé avec succès!")
    
    # 7. Résumé final
    print("\n📊 Résumé du dataset final:")
    print(f"   - Nombre de matchs: {len(df_final)}")
    print(f"   - Période: {df_final['Date'].min()} à {df_final['Date'].max()}")
    print(f"   - Distribution des résultats:")
    print(df_final['Target'].value_counts().to_string())
    
    print("\n🎉 Preprocessing terminé avec succès!")
    print(f"📁 Dataset prêt pour l'entraînement: {PROCESSED_DATASET}")

if __name__ == "__main__":
    main()
