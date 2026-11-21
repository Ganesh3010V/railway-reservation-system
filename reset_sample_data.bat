@echo off
title Reset Railway Sample Data
cd /d "%~dp0"
echo ==========================================================
echo Resetting Railway Reservation Demo Data...
echo Loading 12 sample passengers (8 confirmed, 4 waitlisted)
echo ==========================================================
echo.
python railway\apply_seed.py
pause

