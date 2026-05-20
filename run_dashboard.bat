@echo off
title FirstClub Assignment Category Intelligence Dashboard Server
echo ========================================================
echo  Starting FirstClub Assignment Category Intelligence Dashboard...
echo ========================================================
echo.
python "%~dp0server.py"
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Python failed to start the server. 
    echo Please ensure Python is installed and added to your system PATH.
    echo.
    pause
)
