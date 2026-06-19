@echo off
echo Instalando dependências...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Gerando .exe...
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "TopocadPC" ^
    --add-data "models;models" ^
    --add-data "utils;utils" ^
    --add-data "ui;ui" ^
    --hidden-import ezdxf ^
    --hidden-import matplotlib.backends.backend_qtagg ^
    main.py

echo.
echo Pronto! O executável está em: dist\TopocadPC.exe
pause
