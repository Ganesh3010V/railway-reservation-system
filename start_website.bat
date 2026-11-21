@echo off
title Railway Reservation System
cd /d "%~dp0"

echo ==========================================================
echo Starting Railway Reservation System Website...
echo The website will automatically open at http://localhost:5000
echo (Keep this window open while using the website)
echo ==========================================================
echo.

python railway\app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying with virtual environment python...
    .venv\Scripts\python.exe railway\app.py
)

pause

