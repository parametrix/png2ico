@echo off
REM PNG to ICO Converter - Simple Installer
REM This script creates a simple installation

echo PNG to ICO Converter Installer
echo ===============================

set INSTALL_DIR=%PROGRAMFILES%\PNG to ICO Converter

echo Installing to: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copying files...
copy "main.py" "%INSTALL_DIR%\"
copy "config.ini" "%INSTALL_DIR%\"
copy "README.md" "%INSTALL_DIR%\"

echo Creating desktop shortcut...
set SHORTCUT="%USERPROFILE%\Desktop\PNG to ICO Converter.lnk"
if exist %SHORTCUT% del %SHORTCUT%

REM Create a simple batch file for the shortcut
echo @echo off > "%INSTALL_DIR%\run_app.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\run_app.bat"
echo python main.py >> "%INSTALL_DIR%\run_app.bat"
echo pause >> "%INSTALL_DIR%\run_app.bat"

echo Installation completed!
echo.
echo To run the application:
echo - Use the desktop shortcut
echo - Or run: python "%INSTALL_DIR%\main.py"
echo.
pause