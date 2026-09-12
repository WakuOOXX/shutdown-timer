@echo off
echo ================================
echo    Shutdown Timer - Build Tool
echo ================================
echo.

pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo Building...
echo.

pyinstaller --onefile --windowed --name "ShutdownTimer" --clean main.py

echo.
echo ================================
echo Build complete!
echo Output: dist\ShutdownTimer.exe
echo ================================
echo.

pause
