# Kuittitulostin - Receipt Printer Application

Harjun Raskaskone Oy:n (HRK) kuittisovellus / Receipt application for Harjun Raskaskone Oy.

## Ominaisuudet / Features

- ✅ **Graafinen käyttöliittymä (GUI)** Tkinter-pohjaisella käyttöliittymällä
- ✅ **Terminaalitila** - varmuuskopio, jos GUI ei ole käytettävissä
- ✅ **Tuotteiden hallinta** - lisää ja poista tuotteita helposti
- ✅ **Automaattiset laskutoimitukset** - välisumma, ALV 24%, kokonaissumma
- ✅ **Tulostus oletustulostimeen** - Windows ja Linux -tuki
- ✅ **PNG-tallennus** - tallenna kuitit kuvina
- ✅ **Virheiden käsittely** - sovellus ei kaadu virheellisistä syötteistä
- ✅ **Kaksikielinen** - suomi ja englanti
- ✅ **Yrityksen logo** - ASCII-muotoinen logo kuitissa

## Asennus / Installation

### Windows

1. **Asenna riippuvuudet** - aja `install.bat`:
   ```cmd
   install.bat
   ```
   
   Skripti:
   - Tarkistaa Python-asennuksen (3.8 tai uudempi suositellaan)
   - Asentaa tarvittavat kirjastot: `pillow`, `colorama`
   - Tarjoaa mahdollisuuden käynnistää sovelluksen heti

2. **Käynnistä sovellus**:
   ```cmd
   python receipt_app.py
   ```

### Linux / macOS

1. **Asenna riippuvuudet**:
   ```bash
   pip3 install pillow colorama
   ```

2. **Käynnistä sovellus**:
   ```bash
   python3 receipt_app.py
   ```

3. **Terminaalitila** (jos GUI ei ole käytettävissä):
   ```bash
   python3 receipt_app.py --terminal
   ```

## Käyttö / Usage

### GUI-tila

1. **Lisää tuotteita**:
   - Syötä tuotenimi, määrä ja hinta
   - Paina "Lisää tuote" / "Add Product"

2. **Poista tuotteita**:
   - Valitse tuote listasta
   - Paina "Poista valittu" / "Remove Selected"

3. **Tulosta kuitti**:
   - Paina "Tulosta kuitti" / "Print Receipt"
   - Kuitti lähetetään oletustulostimeen

4. **Tallenna PNG**:
   - Paina "Tallenna PNG" / "Save PNG"
   - Valitse tallennuspaikka

5. **Tyhjennä ostoskori**:
   - Paina "Tyhjennä" / "Clear"

6. **Lopeta**:
   - Paina "Lopeta" / "Exit"

### Terminaalitila

Valitse toiminto numerolla:

1. Lisää tuote - syötä nimi, määrä ja hinta
2. Poista tuote - valitse tuotteen numero
3. Näytä ostoskori - näytä kaikki tuotteet ja yhteenveto
4. Tulosta kuitti - tulosta kuitti tulostimeen
5. Tallenna PNG - tallenna kuitti PNG-tiedostona
6. Tyhjennä - tyhjennä ostoskori
7. Lopeta - sulje sovellus

## Vaatimukset / Requirements

- **Python**: 3.8 tai uudempi (testattu Python 3.12 ja 3.13 kanssa)
- **Kirjastot**:
  - `tkinter` - graafiseen käyttöliittymään (sisältyy useimpiin Python-asennuksiin)
  - `pillow` - PNG-tallennukseen
  - `colorama` - terminaalin väreihin (valinnainen)

## Tulostus / Printing

### Windows
- Käyttää `notepad /p` -komentoa tulostukseen
- Toimii oletustulostimella automaattisesti

### Linux
- Käyttää `lpr`-komentoa tulostukseen
- Varmista, että `lpr` on asennettu: `sudo apt-get install cups-bsd`

### macOS
- Käyttää `lpr`-komentoa tulostukseen
- Toimii oletuksena macOS:ssä

## Tiedostorakenne / File Structure

```
receipt_app.py         # Pääohjelma / Main application
install.bat            # Windows-asennusskripti / Windows installer
test_receipt_app.py    # Testit / Tests
KUITTITULOSTIN_README.md  # Tämä tiedosto / This file
```

## Testit / Tests

Aja testit:
```bash
python3 test_receipt_app.py
```

Testit kattavat:
- Tuotteiden luonnin ja hallinnan
- Laskutoimitusten oikeellisuuden
- PNG-tallennuksen
- Virheiden käsittelyn

## Vianmääritys / Troubleshooting

### "Tkinter ei ole käytettävissä"

**Ratkaisu**: Käytä terminaalitilaa:
```bash
python3 receipt_app.py --terminal
```

Tai asenna Tkinter:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS**: Tkinter sisältyy Python-asennukseen

### "Pillow-kirjasto puuttuu"

**Ratkaisu**: Asenna Pillow:
```bash
pip3 install pillow
```

### "Tulostus epäonnistui"

**Windows**: Varmista, että oletustulostin on määritetty
**Linux**: Asenna `cups-bsd`: `sudo apt-get install cups-bsd`

### Python ei löydy (Windows)

**Ratkaisu**: 
1. Lataa Python: https://www.python.org/downloads/
2. Asenna ja valitse "Add Python to PATH"
3. Käynnistä komentorivi uudelleen

## Tekijänoikeudet / Copyright

© 2024 Harjun Raskaskone Oy (HRK)
Kehittänyt AnomFIN | AnomTools

## Lisenssi / License

Tämä sovellus on luotu Harjun Raskaskone Oy:n sisäiseen käyttöön.
This application is created for internal use by Harjun Raskaskone Oy.
