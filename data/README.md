# Dataset Description

## Structure des données

### data/raw/
- `dataset.csv` : Dataset original avec toutes les statistiques de match

### data/processed/  
- `dataset_final.csv` : Dataset traité avec features d'historique prêt pour l'entraînement

## Features créées

### Features d'historique par équipe
- `home_avg_goals_scored` : Moyenne de buts marqués (équipe domicile)
- `home_avg_goals_conceded` : Moyenne de buts encaissés (équipe domicile)
- `home_avg_shots` : Moyenne de tirs (équipe domicile)
- `home_avg_shots_target` : Moyenne de tirs cadrés (équipe domicile)
- `home_avg_corners` : Moyenne de corners (équipe domicile)
- `home_win_rate` : Taux de victoire (équipe domicile)
- `home_form` : Forme récente en points (équipe domicile)

### Features dérivées
- `form_difference` : Différence de forme entre les équipes
- `goal_difference` : Différence de goal average
- `home_shot_efficiency` : Efficacité des tirs (équipe domicile)
- `away_shot_efficiency` : Efficacité des tirs (équipe extérieur)
- `home_advantage` : Avantage du terrain

### Variable cible
- `Target` : Résultat du match (H=Home win, D=Draw, A=Away win)
- `Target_encoded` : Version encodée (0=H, 1=D, 2=A)

## Méthodologie

Les features sont créées en utilisant l'historique des N derniers matchs de chaque équipe **avant** le match à prédire, respectant ainsi la contrainte temporelle.
