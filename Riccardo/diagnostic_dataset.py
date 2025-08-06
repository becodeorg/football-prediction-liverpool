import pandas as pd
import os

print("=== DIAGNOSTIC DATASET ===")

# Test 1: Vérifier l'existence du fichier
paths_to_test = ['../dataset.csv', './dataset.csv', 'dataset.csv']

for path in paths_to_test:
    exists = os.path.exists(path)
    print(f"Fichier '{path}': {'✅ EXISTE' if exists else '❌ N EXISTE PAS'}")
    
    if exists:
        size = os.path.getsize(path)
        print(f"  Taille: {size} bytes")

print("\n=== TEST CHARGEMENT ===")

# Test 2: Essayer de charger avec différents encodages
encodings = ['latin-1', 'utf-8', 'cp1252', 'iso-8859-1']

for path in ['../dataset.csv', './dataset.csv']:
    if os.path.exists(path):
        print(f"\n📁 Test du fichier: {path}")
        
        for encoding in encodings:
            try:
                data = pd.read_csv(path, encoding=encoding, nrows=5)  # Test avec seulement 5 lignes
                print(f"  ✅ {encoding}: OK - {len(data)} lignes chargées")
                print(f"     Colonnes: {list(data.columns[:5])}...")
                break
            except Exception as e:
                print(f"  ❌ {encoding}: {str(e)[:50]}...")
        else:
            print(f"  ❌ Tous les encodages ont échoué pour {path}")

print("\n=== FIN DIAGNOSTIC ===")
