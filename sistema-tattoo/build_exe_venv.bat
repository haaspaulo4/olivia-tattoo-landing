@echo off
echo ============================================
echo   Compilando num VENV (Modo Rapido)
echo ============================================
echo.

if not exist venv_build\ (
    echo Criando ambiente virtual limpo...
    python -m venv venv_build
)

echo Ativando venv e instalando dependencias (isso evita puxar gigabytes de lixo do seu PC)...
call venv_build\Scripts\activate
pip install -r requirements.txt pyinstaller

echo.
echo Limpando build anterior...
if exist dist\ ( rmdir /s /q dist )
if exist build\ ( rmdir /s /q build )

echo.
echo Gerando executavel super rapido...
echo.

pyinstaller ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "Sistema-OliviaTattoo" ^
    --icon "app_icon.ico" ^
    --add-data "app_icon.ico;." ^
    --add-data "database;database" ^
    --add-data "utils;utils" ^
    --add-data "models;models" ^
    --add-data "views;views" ^
    --add-data "assets;assets" ^
    --hidden-import customtkinter ^
    --hidden-import PIL ^
    --hidden-import PIL._tkinter_finder ^
    --collect-all neonize ^
    main.py

echo.
if exist "dist\Sistema-OliviaTattoo.exe" (
    echo ============================================
    echo   Executavel gerado na velocidade da luz!
    echo   Local: dist\Sistema-OliviaTattoo.exe
    echo ============================================
) else (
    echo [ERROR] Falha.
)
