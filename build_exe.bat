@echo off
echo Instalando dependências...
pip install -r requirements.txt
pip install pyinstaller pillow

echo.
echo Gerando ícone...
python create_icon.py

echo.
echo Gerando .exe...
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "TopocadPC" ^
    --icon "topocad.ico" ^
    --add-data "topocad.ico;." ^
    --add-data "models;models" ^
    --add-data "utils;utils" ^
    --add-data "ui;ui" ^
    --hidden-import ezdxf ^
    --hidden-import matplotlib.backends.backend_qtagg ^
    main.py

echo.
echo Compilando instalador...
set INNO="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist %INNO% (
    %INNO% topocad_installer.iss
    echo.
    echo Instalador gerado em: installer\TopocadPC_Setup.exe
) else (
    echo [AVISO] Inno Setup não encontrado. Apenas o .exe foi gerado em dist\TopocadPC.exe
    echo Para gerar o instalador, instale o Inno Setup 6: https://jrsoftware.org/isinfo.php
)

echo.
echo Pronto!
pause
