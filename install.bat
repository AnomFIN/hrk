@echo off
REM ================================================================
REM Kuittitulostin - Asennusskripti / Receipt Printer - Install Script
REM Harjun Raskaskone Oy (HRK)
REM ================================================================

echo.
echo ===============================================
echo   KUITTITULOSTIN - ASENNUS
echo   RECEIPT PRINTER - INSTALLATION
echo ===============================================
echo.

REM Tarkista Python-asennus / Check Python installation
echo Tarkistetaan Python-asennus...
echo Checking Python installation...
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [VIRHE] Python ei loytynyt!
    echo [ERROR] Python not found!
    echo.
    echo Lataa Python osoitteesta: https://www.python.org/downloads/
    echo Download Python from: https://www.python.org/downloads/
    echo.
    echo Varmista, etta valitset "Add Python to PATH" asennuksen aikana!
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo [OK] Python loytyi / Python found
echo.

REM Tarkista Python-versio / Check Python version
echo Tarkistetaan Python-versio...
echo Checking Python version...
python --version
echo.

REM Tarkista pip / Check pip
echo Tarkistetaan pip...
echo Checking pip...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [VAROITUS] pip ei loytynyt, yritetaan asentaa...
    echo [WARNING] pip not found, trying to install...
    python -m ensurepip --default-pip
    if %ERRORLEVEL% neq 0 (
        echo [VIRHE] pip:n asennus epaonnistui!
        echo [ERROR] Failed to install pip!
        pause
        exit /b 1
    )
)

echo [OK] pip loytyi / pip found
echo.

REM Paivita pip / Update pip
echo Paivitetaan pip...
echo Updating pip...
python -m pip install --upgrade pip
echo.

REM Asenna riippuvuudet / Install dependencies
echo ===============================================
echo   ASENNETAAN RIIPPUVUUDET
echo   INSTALLING DEPENDENCIES
echo ===============================================
echo.

echo Asennetaan Pillow (kuvankasittely)...
echo Installing Pillow (image processing)...
python -m pip install pillow
if %ERRORLEVEL% neq 0 (
    echo [VAROITUS] Pillow:n asennus epaonnistui!
    echo [WARNING] Failed to install Pillow!
    echo PNG-tallennus ei toimi ilman Pillow:ta.
    echo PNG save will not work without Pillow.
    echo.
) else (
    echo [OK] Pillow asennettu / Pillow installed
    echo.
)

echo Asennetaan colorama (terminaalivari)...
echo Installing colorama (terminal colors)...
python -m pip install colorama
if %ERRORLEVEL% neq 0 (
    echo [VAROITUS] colorama:n asennus epaonnistui!
    echo [WARNING] Failed to install colorama!
    echo Terminaalitila toimii ilman varijakin.
    echo Terminal mode will work without colors.
    echo.
) else (
    echo [OK] colorama asennettu / colorama installed
    echo.
)

REM Tarkista, onko tkinter kaytettavissa / Check if tkinter is available
echo Tarkistetaan tkinter (GUI-kirjasto)...
echo Checking tkinter (GUI library)...
python -c "import tkinter" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [VAROITUS] tkinter ei ole kaytettavissa!
    echo [WARNING] tkinter is not available!
    echo GUI-tila ei toimi. Kayta terminaalitilaa: python receipt_app.py --terminal
    echo GUI mode will not work. Use terminal mode: python receipt_app.py --terminal
    echo.
) else (
    echo [OK] tkinter loytyi / tkinter found
    echo.
)

REM Nayta yhteenveto / Show summary
echo.
echo ===============================================
echo   ASENNUS VALMIS!
echo   INSTALLATION COMPLETE!
echo ===============================================
echo.
echo Voit nyt kayttaa ohjelmaa / You can now run the program:
echo.
echo   GUI-tila (suositeltu):
echo   GUI mode (recommended):
echo     python receipt_app.py
echo.
echo   Terminaalitila:
echo   Terminal mode:
echo     python receipt_app.py --terminal
echo.
echo ===============================================
echo.

REM Kysy, kaynnistetaanko ohjelma / Ask if to start the program
set /p START="Kaynnistetaanko ohjelma nyt? (k/e) / Start program now? (y/n): "
if /i "%START%"=="k" goto start_program
if /i "%START%"=="y" goto start_program
goto end

:start_program
echo.
echo Kaynnistetaan kuittitulostin...
echo Starting receipt printer...
echo.
python receipt_app.py
goto end

:end
pause
