@echo off
title Sugo Grand Palace Hotel - System Launcher
cls
echo ==============================================================
echo       SUGO GRAND PALACE HOTEL - RESERVATION SYSTEM
echo ==============================================================
echo.
echo  Choose how you would like to run the system:
echo.
echo   [1] Native Desktop Window (pywebview with HTML5 & CSS3) - DEFAULT
echo   [2] Web Browser Mode (http://127.0.0.1:5000)
echo   [3] Terminal / CLI Mode
echo.
set /p choice="Enter your choice (1, 2, or 3) [Default: 1]: "
if "%choice%"=="2" goto BROWSER
if "%choice%"=="3" goto CLI
goto WEBVIEW

:WEBVIEW
echo Starting Native Desktop Window with pywebview...
python main.py
goto END

:BROWSER
echo Starting Web Browser Mode at http://127.0.0.1:5000 ...
python main.py --browser
goto END

:CLI
python main.py --cli
goto END

:END
pause
