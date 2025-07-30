@echo off
REM Script de lancement Football Prediction App V2.0

echo 🚀 Lancement de Football Prediction App V2.0
echo =============================================
echo.
echo 📊 Fonctionnalités incluses :
echo   ✅ Dashboard professionnel avec thèmes
echo   ✅ Graphiques interactifs Plotly
echo   ✅ Système de notifications avancé
echo   ✅ Prédictions multi-matchs
echo   ✅ Comparaison bookmakers
echo   ✅ Historique ^& performance
echo.
echo 🌐 Démarrage du serveur Streamlit...
echo.

streamlit run football_prediction_app_v2.py --server.port 8540
