@echo off
echo ===================================================
echo INSTALLATION ET LANCEMENT DU DASHBOARD PDP
echo ===================================================

REM Se placer dans le dossier du script
cd /d "%~dp0"

echo.
echo 1. Verification des dependances...
echo -----------------------------------
pip install -r dashboard/requirements.txt

echo.
echo 2. Lancement de l'application...
echo -----------------------------------
python -m streamlit run dashboard/app.py

if %errorlevel% neq 0 (
    echo.
    echo ERREUR : Le lancement a echoue. Verifiez que Python est bien installe et dans le PATH.
    echo.
    pause
)
