# LV Electronics - Kuittisovellus

Täydellinen kuittisovellus LV Electronics -yritykselle, joka sisältää sekä Python-version että web-version.

## 📦 Tiedostot

### Python-sovellus (Pääsovellus)
- **`receipt_app.py`** - Täydellinen kuittisovellus (GUI + terminaali)
- **`install.bat`** - Asennusskripti Windows 11:lle

### Web-kassa
- **`web-kassa.html`** - Modernin web-kassa HTML/CSS/JavaScript
- **`admin/kuitti-api.php`** - PHP-backend kuittien käsittelyyn

## 🚀 Käyttöönotto

### Python-sovellus (Windows 11)

1. **Asenna riippuvuudet:**
   ```batch
   install.bat
   ```

2. **Käynnistä sovellus:**
   ```batch
   python receipt_app.py
   ```

### Web-kassa

1. **Kopioi tiedostot web-palvelimelle**
2. **Varmista PHP-tuki palvelimella**
3. **Avaa `web-kassa.html` selaimessa**

## ✨ Ominaisuudet

### Python-sovellus
- 🖥️ **Tkinter GUI** - Moderni käyttöliittymä
- 📟 **Terminaaliversio** - Varalla jos GUI ei toimi
- ➕ **Tuotteiden hallinta** - Lisää/poista tuotteita
- 💰 **ALV-laskenta** - Automaattinen 24% ALV
- 🖨️ **Tulostus** - Oletustulostimeen (Windows/Linux)
- 💾 **PNG-tallennus** - Pillow-kirjastolla
- 🎨 **ASCII-logo** - LV-tyylinen logo kuiteissa
- ⚡ **Virheenkäsittely** - Ei kaadu virheistä

### Web-kassa
- 🌐 **Responsiivinen** - Toimii kaikilla laitteilla
- ⚡ **Reaaliaikainen** - Summat päivittyvät automaattisesti
- 📄 **Kuitti-esikatselu** - Näe kuitti ennen tulostusta
- 🖨️ **Web-tulostus** - Tulosta suoraan selaimesta
- 📱 **Mobiilioptimoitu** - Toimii puhelimella ja tabletilla
- 🎨 **Moderni UI** - Gradientit ja animaatiot
- ⌨️ **Näppäinkomentoja** - Enter = lisää, Ctrl+P = tulosta

## 💻 Tekniset yksityiskohdat

### Python-sovellus
- **Python 3.7+** (testattu 3.13:lla)
- **Riippuvuudet:** Pillow, colorama
- **GUI:** Tkinter (sisäänrakennettu)
- **Tulostus:** Windows (notepad /p), Linux (lp/lpr)
- **Kuvat:** PNG-tallennus Pillow:lla

### Web-kassa
- **Frontend:** Vanilla JavaScript (ei frameworkkeja)
- **Backend:** PHP 7.4+ (valinnainen)
- **Tietokanta:** Ei tarvita (tiedostopohjainen)
- **Tulostus:** Browser print API
- **Responsiivinen:** CSS Grid + Flexbox

## 📋 Käyttöohjeet

### Python-version GUI:

1. **Lisää tuotteita** lomakkeen kautta
2. **Poista tuotteita** valitsemalla listasta
3. **Tarkista summat** automaattisesti päivittyvät
4. **Tulosta kuitti** 🖨️ -napilla
5. **Tallenna PNG** 💾 -napilla
6. **Lopeta** ❌ -napilla turvallisesti

### Web-kassan käyttö:

1. **Lisää tuotteita** yläosan lomakkeella
2. **Tarkista esikatselu** oikean puolen ruudusta
3. **Tulosta kuitti** 🖨️ -napilla (avaa tulostusikkunan)
4. **Tyhjennä kuitti** 🗑️ -napilla uutta varten

## 🔧 Konfigurointi

### Yritystiedot (receipt_app.py):
```python
YRITYS_NIMI = "LV Electronics"
YRITYS_OSOITE = "Hämeentie 123, 00500 Helsinki"
YRITYS_PUHELIN = "Tel: +358 50 123 4567"
YRITYS_Y_TUNNUS = "Y-tunnus: 1234567-8"
ALV_KANTA = Decimal('0.24')  # 24% ALV
```

### Web-kassan asetukset (web-kassa.html):
```javascript
// Muokkaa yritystietoja HTML:n header-osiossa
// ALV-kanta: 24% (JavaScript-koodissa)
```

## 🛠️ Vianmääritys

### Python-sovellus:

**GUI ei käynnisty:**
- Tarkista Tkinter-asennus: `python -c "import tkinter"`
- Käytä terminaaliversiota automaattisesti

**Tulostus ei toimi:**
- Windows: Tarkista oletustulostin
- Linux: Asenna `lp` tai `lpr`: `sudo apt install cups-client`

**PNG-tallennus ei toimi:**
- Asenna Pillow: `pip install pillow`

### Web-kassa:

**Kuitti ei tulostu:**
- Tarkista selaimesi tulostusasetukset
- Salli ponnahdusikkunat sivustolle
- Kokeile Ctrl+P manuaalisesti

## 📄 Lisenssit ja tekijänoikeudet

**LV Electronics Kuittisovellus**
- Tekijä: GitHub Copilot (Claude Sonnet 4)
- Käyttötarkoitus: LV Electronics -yrityksen kassajärjestelmä
- Sisältää: ASCII-logo, yritystiedot, ALV-laskennat

**Käytetyt kirjastot:**
- Python: Tkinter (PSF), Pillow (PIL License), colorama (BSD)
- Web: Vanilla JavaScript (ei ulkoisia kirjastoja)

---

**© 2025 LV Electronics - Kuittisovellus**