@echo off
REM ==================================================================
REM  AE_UNITS - build one-file .exe with PyInstaller
REM  Requires:  pip install pyinstaller pillow customtkinter
REM  Result:    dist\AE_UNITS.exe
REM ==================================================================

python -m PyInstaller --noconfirm main.spec
if errorlevel 1 (
  echo Build failed - see output above.
  exit /b 1
)
echo.
if exist dist\AE_UNITS.exe (
  echo Done:  dist\AE_UNITS.exe
) else (
  echo Build finished but dist\AE_UNITS.exe not found.
  exit /b 1
)
