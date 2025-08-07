@echo off
echo.
echo ======================================
echo    ⚽ FOOTBALL PREDICTION SUITE v2.0
echo ======================================
echo.
echo 🚀 Démarrage de l'application avancée...
echo 📊 Chargement des modules d'analyse...
echo.

REM Vérifier si nous sommes dans le bon dossier
if not exist "Riccardo" (
    echo ❌ Erreur: Dossier Riccardo non trouvé
    echo 📁 Veuillez lancer ce script depuis le dossier racine du projet
    pause
    exit /b 1
)

REM Démarrer l'application principale
echo ✅ Lancement de Football Prediction Suite...
streamlit run Riccardo/app_suite.py --server.port 8508

REM Si une erreur survient
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erreur lors du démarrage de l'application
    echo 💡 Suggestions:
    echo   - Vérifiez que Streamlit est installé: pip install streamlit
    echo   - Installez les dépendances: pip install -r Riccardo/requirements_pro.txt
    echo   - Vérifiez que le fichier dataset.csv est présent
    echo.
    pause
)
