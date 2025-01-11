@echo off
echo Installing required Python packages...
pip install tkinterdnd2 py7zr rarfile

echo.
echo Starting KOTOR Mod Installer...
python kotor_mod_installer.py

pause