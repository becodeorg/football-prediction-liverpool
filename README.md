# ⚽ Football Match Prediction System

## ��� Description

Système de prédiction de matchs de football utilisant l'intelligence artificielle pour prédire les résultats de futurs matchs basé sur les performances historiques des équipes.

## ��� Fonctionnalités

- **Prédiction de futurs matchs** avec analyse par saison
- **Interface Streamlit** interactive et conviviale
- **Modèle Random Forest** avec paramètres optimisés (tirs cadrés, tirs totaux, corners)
- **Sélection flexible des saisons** pour l'analyse
- **Statistiques détaillées** par équipe et par saison
- **Analyse avancée** des performances domicile/extérieur

## ��� Dataset

- **Ligue :** Jupiler Pro League (Belgique)
- **Période :** 2019-20 à 2024-25 (6 saisons)
- **Matchs :** 1,508 matchs analysés
- **Variables :** HST, AST, HS, AS, HC, AC, FTHG, FTAG, FTR

## ���️ Installation

1. **Cloner le projet**
\`\`\`bash
git clone [repository-url]
cd football_prediction_clean
\`\`\`

2. **Installer les dépendances**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## ��� Utilisation

### Interface Web (Recommandé)
\`\`\`bash
streamlit run football_prediction_app.py
\`\`\`
Puis ouvrir http://localhost:8501 dans votre navigateur

### Analyse dans Jupyter
\`\`\`bash
jupyter notebook football_analysis.ipynb
\`\`\`

## ��� Structure du Projet

\`\`\`
football_prediction_clean/
├── dataset.csv                    # Données des matchs
├── football_prediction_app.py     # Application Streamlit
├── football_analysis.ipynb        # Notebook d'analyse
├── requirements.txt               # Dépendances Python
└── README.md                      # Documentation
\`\`\`

## ��� Modèle

- **Algorithme :** Random Forest (100 arbres)
- **Features :** 3 variables par équipe
  - Tirs cadrés moyens (HST/AST)
  - Tirs totaux moyens (HS/AS)  
  - Corners moyens (HC/AC)
- **Distinction :** Performances domicile vs extérieur
- **Validation :** Entraînement sur données historiques

## ��� Prédictions

Le système analyse :
- ✅ Moyennes historiques des équipes
- ✅ Avantage du terrain (domicile/extérieur)
- ✅ Corrélations entre statistiques offensives
- ✅ Performances par saison sélectionnée

## ⚠️ Limitations

- Ne prend pas en compte la forme récente
- Ignore les blessures/suspensions/transferts
- Basé uniquement sur les données historiques
- Prédictions probabilistes, pas des certitudes

## ��� Résultats

Le modèle fournit :
- **Score prédit** pour chaque équipe
- **Niveau de confiance** de la prédiction
- **Type de match** (offensif/défensif/équilibré)
- **Statistiques détaillées** utilisées pour la prédiction

## ��� Contact

Projet développé pour l'analyse et la prédiction de matchs de football.

---
*Utilisez ce système de manière responsable. Les prédictions sont basées sur des données historiques et ne garantissent aucun résultat.*
