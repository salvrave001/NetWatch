@echo off
setlocal
cd /d "%~dp0"

echo === NetWatch build ===
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    exit /b 1
)

if not exist "assets\netwatch.ico" (
    echo [ERROR] Missing assets\netwatch.ico
    exit /b 1
)
if not exist "assets\logo_header.png" (
    echo [ERROR] Missing assets\logo_header.png
    exit /b 1
)

echo [1/3] Installing dependencies...
python -m pip install -r requirements.txt pyinstaller -q
if errorlevel 1 (
    echo [ERROR] pip install failed.
    exit /b 1
)

echo [2/3] Building NetWatch.exe...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --onefile ^
    --name NetWatch ^
    --icon "assets\netwatch.ico" ^
    --add-data "assets;assets" ^
    --collect-all customtkinter ^
    --hidden-import process_checker ^
    --hidden-import process_checker.app ^
    --hidden-import process_checker.network ^
    --hidden-import process_checker.ui ^
    --hidden-import process_checker.theme ^
    --hidden-import process_checker.i18n ^
    --hidden-import process_checker.paths ^
    main.py

if errorlevel 1 (
    echo [ERROR] Build failed.
    exit /b 1
)

echo.
echo [3/3] Done.
echo EXE: "%~dp0dist\NetWatch.exe"
echo.
exit /b 0
