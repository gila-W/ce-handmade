@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo מעבד תמונות...
py process-images.py
echo.
pause
