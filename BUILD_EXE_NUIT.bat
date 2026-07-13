@echo off
REM ==================================================================
REM  AE_UNITS - build jednosouboroveho .exe pomoci Nuitka
REM ------------------------------------------------------------------
REM  Vyzaduje:  pip install nuitka
REM  C kompilator (MinGW-w64) si Nuitka pri prvnim behu sama stahne
REM  diky prepinaci --assume-yes-for-downloads.
REM
REM  Vysledek:  build\AE_UNITS.exe   (adresar build\ je v .gitignore)
REM  Build trva radove minuty, hlavne pri prvnim spusteni.
REM ==================================================================

python -m nuitka ^
  --standalone ^
  --onefile ^
  --enable-plugin=tk-inter ^
  --include-package-data=customtkinter ^
  --include-data-files=icon.ico=icon.ico ^
  --include-data-files=icon.png=icon.png ^
  --windows-console-mode=disable ^
  --windows-icon-from-ico=icon.ico ^
  --company-name=AE_UNITS ^
  --product-name=AE_UNITS ^
  --product-version=0.41 ^
  --output-dir=build ^
  --output-filename=AE_UNITS.exe ^
  --assume-yes-for-downloads ^
  --remove-output ^
  main.py

echo.
if exist build\AE_UNITS.exe (
  echo Hotovo:  build\AE_UNITS.exe
) else (
  echo Build selhal - zkontrolujte vypis vyse.
)
pause
