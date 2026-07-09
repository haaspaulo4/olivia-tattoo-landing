@echo off
title Olivia Tattoo - Sistema de Gestao
color 0A
cls
echo ============================================
echo      OLIVIA TATTOO - Sistema de Gestao
echo ============================================
echo.
echo Iniciando o sistema...
echo.

"C:\Users\Paulo\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0main.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Nao foi possivel iniciar o sistema.
    echo Verifique se o Python esta instalado em:
    echo C:\Users\Paulo\AppData\Local\Programs\Python\Python312\
    echo.
    pause
)