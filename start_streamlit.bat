@echo off
title Railway Reservation System (Streamlit)
cd /d "%~dp0"

echo ==========================================================
echo Starting Streamlit App...
echo ==========================================================
echo.

streamlit run app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying with virtual environment streamlit...
    .venv\Scripts\streamlit.exe run app.py
)

pause

