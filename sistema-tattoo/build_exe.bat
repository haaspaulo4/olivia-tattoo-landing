@echo off
echo ============================================
echo   Compilando Sistema de Gestao - Olivia Tattoo
echo ============================================
echo.

REM Verificar se PyInstaller está instalado
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

REM Instalar dependências
echo Instalando dependencias...
pip install -r requirements.txt

REM Limpar build anterior
if exist dist\ (
    rmdir /s /q dist
)
if exist build\ (
    rmdir /s /q build
)

echo.
echo Gerando executavel...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "OliviaTattoo-Gestao" ^
    --icon NONE ^
    --add-data "database;database" ^
    --add-data "utils;utils" ^
    --add-data "models;models" ^
    --add-data "views;views" ^
    --add-data "assets;assets" ^
    --hidden-import customtkinter ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    main.py

echo.
if exist "dist\OliviaTattoo-Gestao.exe" (
    echo ============================================
    echo   Executavel gerado com sucesso!
    echo.
    echo   Localizacao: dist\OliviaTattoo-Gestao.exe
    echo ============================================
) else (
    echo [ERROR] Falha ao gerar executavel.
)

pause