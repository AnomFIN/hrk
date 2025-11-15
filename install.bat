@echo off
REM ===============================================
REM Kuittisovellus - Asennusskripti Windows 11
REM Tarkistaa Python-version ja asentaa riippuvuudet
REM ===============================================

echo.
echo ================================================
echo   KUITTISOVELLUS - ASENNUSSKRIPTI
echo   LV Electronics
echo ================================================
echo.

REM Tarkista, onko Python asennettu
echo [1/4] Tarkistetaan Python-asennus...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [VIRHE] Python ei ole asennettu tai ei loydy PATH-muuttujasta!
    echo.
    echo Lataa Python osoitteesta: https://www.python.org/downloads/
    echo Muista valita "Add Python to PATH" asennuksen aikana!
    echo.
    pause
    exit /b 1
)

REM Näytä Python-versio
echo.
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Loytyi: %PYTHON_VERSION%

REM Tarkista Python-versio (3.7 tai uudempi suositeltu)
python -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [VAROITUS] Python-versio on vanhempi kuin 3.7
    echo Sovellus saattaa toimia, mutta suositellaan paivitysta.
    echo.
)

REM Tarkista pip
echo.
echo [2/4] Tarkistetaan pip (Python-pakettien hallintaohjelma)...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [VIRHE] pip ei ole kaytettavissa!
    echo Yrita asentaa pip komennolla: python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)

echo Pip on kaytettavissa.

REM Päivitä pip (valinnainen mutta suositeltu)
echo.
echo [3/4] Paivitetaan pip uusimpaan versioon...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [VAROITUS] pip:in paivitys epaonnistui, jatketaan silti...
)

REM Asenna riippuvuudet
echo.
echo [4/4] Asennetaan riippuvuudet...
echo.
echo Asennetaan: Pillow (PNG-kuvatuki)
python -m pip install pillow
if %errorlevel% neq 0 (
    echo [VAROITUS] Pillow:n asennus epaonnistui!
    echo PNG-tallennus ei valttamatta toimi.
    echo.
)

echo.
echo Asennetaan: colorama (varillinen terminaali)
python -m pip install colorama
if %errorlevel% neq 0 (
    echo [VAROITUS] colorama:n asennus epaonnistui!
    echo Terminaaliversio toimii ilman varitystakin.
    echo.
)

REM Tarkista Tkinter (pitäisi tulla Pythonin mukana)
echo.
echo Tarkistetaan Tkinter (GUI-kirjasto)...
python -c "import tkinter" 2>nul
if %errorlevel% neq 0 (
    echo [VAROITUS] Tkinter ei ole kaytettavissa!
    echo GUI ei toimi, mutta terminaaliversio toimii.
    echo.
    echo Windows-asennuksessa Tkinter tulee yleensa Pythonin mukana.
    echo Jos haluat GUI:n, asenna Python uudelleen ja varmista,
    echo etta valitset "tcl/tk and IDLE" -komponentin.
    echo.
) else (
    echo Tkinter on kaytettavissa - GUI toimii!
)

REM Yhteenveto
echo.
echo ================================================
echo   ASENNUS VALMIS!
echo ================================================
echo.
echo Asennetut kirjastot:
python -m pip list | findstr /i "pillow colorama"
echo.
echo Voit nyt kaynnistaa sovelluksen komennolla:
echo   python receipt_app.py
echo.
echo tai kaksoisnapsauttamalla receipt_app.py -tiedostoa
echo (jos Python on liitetty .py-tiedostoihin).
echo.
echo ================================================
echo.
pause
