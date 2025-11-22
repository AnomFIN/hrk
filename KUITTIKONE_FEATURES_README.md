# Kuittikone - Uudet ominaisuudet / New Features

## Yleiskatsaus / Overview

Kuittikone on nyt päivitetty offline-toimivalla kuittitulostusjärjestelmällä, joka tukee muokattavia asetuksia, maksutietoja ja ASCII-logon generointia. Kaikki ominaisuudet toimivat täysin offline-tilassa ilman internet-yhteyttä.

Receipt printer application has been upgraded with offline-capable receipt printing system that supports editable settings, payment information, and ASCII logo generation. All features work completely offline without internet connection.

## 🆕 Uudet ominaisuudet / New Features

### 1. ✨ ASCII Logo Generator
Luo mukautettuja ASCII-logoja eri tyyleillä / Create custom ASCII logos with different styles:

- **Box** - Laatikkoreunukset / Box borders (╔═══╗)
- **Stars** - Tähtireunukset / Star borders (***)
- **Double** - Kaksoisviiva / Double line (═══)
- **Simple** - Yksinkertainen / Simple (===)
- **Banner** - Banneri / Banner style (┌───┐)

**Käyttö / Usage:**
```python
from receipt_app import ASCIILogoGenerator

# Luo logo
logo = ASCIILogoGenerator.generate("HRK", "box")
print(logo)

# Output:
# ╔═══════╗
# ║  HRK  ║
# ╚═══════╝
```

### 2. 💳 Maksutiedot / Payment Information
Lisää kattavat maksutiedot kuitteihin / Add comprehensive payment information to receipts:

- Maksutapa / Payment method (Käteinen, Kortti, Lasku, Verkkopankki)
- Korttitype / Card type (Visa, MasterCard, etc.)
- Tapahtumatunnus / Transaction ID
- Pankkiviite / Bank reference

**Käyttö / Usage:**
```python
receipt = Receipt()
receipt.set_payment_info(
    method="Kortti / Card",
    card_type="Visa Debit",
    transaction_id="TX-2024-001234",
    bank_reference="RF1234567890"
)
```

### 3. 💾 Offline-tallennus / Offline Storage
Tallenna kuitit paikallisesti ja hallinnoi historiaa / Save receipts locally and manage history:

- Automaattinen tallennuskansi (`kuitit_offline/`)
- JSON-muotoinen data
- Tekstimuotoiset kuitit (.txt)
- Kuittihistoria
- Lataa vanhat kuitit

**Käyttö / Usage:**
```python
from receipt_app import OfflineStorage

storage = OfflineStorage()

# Tallenna kuitti
if storage.save_receipt(receipt):
    print("Tallennettu!")

# Lataa historia
history = storage.load_history()
for entry in history:
    print(f"{entry['timestamp']}: {entry['total']:.2f} €")

# Lataa vanha kuitti
old_receipt = storage.load_receipt("kuitti_20241122_123456.json")
```

### 4. ⚙️ Muokattavat yritystiedot / Editable Company Info
Muokkaa yrityksen tietoja dynaamisesti / Edit company information dynamically:

- Yrityksen nimi / Company name
- Y-tunnus / Business ID
- Osoite / Address
- Puhelin / Phone
- Sähköposti / Email
- Verkkosivu / Website

**Käyttö / Usage:**
```python
receipt.update_company_info(
    name="Uusi Yritys Oy",
    business_id="FI12345678",
    address="Uusi osoite 1",
    phone="+358 40 123 4567",
    email="info@uusi.fi",
    website="www.uusi.fi"
)
```

### 5. 📋 Kuittihistoria / Receipt History
Selaa ja hallinnoi aiemmin tallennettuja kuitteja / Browse and manage previously saved receipts:

- Näytä kaikki tallennetut kuitit
- Lataa vanha kuitti uudelleen
- Poista vanhat kuitit
- Hakutoiminnot

### 6. 📝 Lisähuomiot / Additional Notes
Lisää vapaita huomioita kuitteihin / Add free-form notes to receipts:

```python
receipt.receipt_notes = "Toimitus huomenna klo 10:00"
```

### 7. 🔄 Kuittien vienti ja tuonti / Receipt Export and Import
Vie ja tuo kuitteja JSON-muodossa / Export and import receipts in JSON format:

```python
# Vie
receipt_data = receipt.to_dict()

# Tuo
loaded_receipt = Receipt.from_dict(receipt_data)
```

## 🚀 Käyttöönotto / Getting Started

### Perusasennus / Basic Installation

```bash
# Kloonaa repositorio
git clone https://github.com/AnomFIN/hrk.git
cd hrk

# Asenna riippuvuudet (valinnainen)
pip install pillow colorama  # PNG-tallennus ja värit

# Käynnistä sovellus
python receipt_app.py
```

### GUI-tila / GUI Mode
Jos Tkinter on asennettu, sovellus käynnistyy graafisessa tilassa:

```bash
python receipt_app.py
```

Uudet painikkeet:
- **💾 Tallenna offline** - Tallenna kuitti offline-tilaan
- **⚙️ Asetukset** - Muokkaa yritystietoja, maksutietoja, logoa ja huomioita
- **📋 Historia** - Selaa tallennettuja kuitteja

### Terminaalitila / Terminal Mode
Käynnistä terminaalitilassa:

```bash
python receipt_app.py --terminal
```

Uudet valikkovaihtoehdot:
- `6` - 💾 Tallenna offline
- `7` - ⚙️ Asetukset
- `8` - 📋 Historia

## 📂 Offline-tallennusrakenne / Offline Storage Structure

```
kuitit_offline/
├── kuitti_historia.json          # Kuittihistoria / Receipt history
├── kuitti_20241122_123456.json   # Kuitti JSON-muodossa
├── kuitti_20241122_123456.txt    # Kuitti tekstimuodossa
├── kuitti_20241122_140530.json
└── kuitti_20241122_140530.txt
```

### Historia-tiedoston rakenne / History File Structure

```json
[
  {
    "timestamp": "2024-11-22T12:34:56",
    "filename": "kuitti_20241122_123456.json",
    "total": 1054.00,
    "company": "Harjun Raskaskone Oy",
    "payment_method": "Kortti / Card"
  }
]
```

### Kuitti-tiedoston rakenne / Receipt File Structure

```json
{
  "timestamp": "2024-11-22T12:34:56",
  "company_info": {
    "name": "Harjun Raskaskone Oy",
    "business_id": "FI12345678",
    "address": "Teollisuustie 1, 00100 Helsinki",
    "phone": "+358 40 123 4567",
    "email": "info@hrk.fi",
    "website": "www.hrk.fi"
  },
  "payment_info": {
    "method": "Kortti / Card",
    "card_type": "Visa Debit",
    "transaction_id": "TX-2024-001234",
    "bank_reference": "RF1234567890"
  },
  "products": [
    {
      "name": "Kaivinkone 15t",
      "quantity": 1,
      "price": 850.00
    }
  ],
  "subtotal": 850.00,
  "vat": 204.00,
  "total": 1054.00,
  "custom_logo": "╔═══════╗\n║  HRK  ║\n╚═══════╝",
  "logo_style": "box",
  "receipt_notes": "Toimitus huomenna"
}
```

## 🎯 Käyttötapaukset / Use Cases

### Esimerkki 1: Peruskuitti maksutiedoilla
```python
from receipt_app import Receipt

receipt = Receipt()
receipt.add_product("Kaivinkone", 1, 850.00)
receipt.set_payment_info(
    method="Kortti / Card",
    card_type="Visa",
    transaction_id="TX-001"
)

print(receipt.generate_text())
```

### Esimerkki 2: Mukautettu logo ja offline-tallennus
```python
from receipt_app import Receipt, OfflineStorage

receipt = Receipt()
receipt.set_custom_logo("HARJUN RASKASKONE", "banner")
receipt.add_product("Kuorma-auto", 2, 450.00)

storage = OfflineStorage()
storage.save_receipt(receipt)
```

### Esimerkki 3: Lataa ja muokkaa vanhaa kuittia
```python
storage = OfflineStorage()
old_receipt = storage.load_receipt("kuitti_20241122_123456.json")

# Lisää tuote
old_receipt.add_product("Lisäpalvelu", 1, 50.00)

# Tallenna uutena kuittina
storage.save_receipt(old_receipt)
```

## 🔧 API-dokumentaatio / API Documentation

### ASCIILogoGenerator

```python
class ASCIILogoGenerator:
    @staticmethod
    def generate(text: str, style: str = "box") -> str:
        """
        Generoi ASCII-logo
        
        Args:
            text: Logo-teksti
            style: Tyyli (box, stars, double, simple, banner)
        
        Returns:
            ASCII-logo merkkijonona
        """
```

### OfflineStorage

```python
class OfflineStorage:
    def __init__(self, storage_dir: str = "kuitit_offline"):
        """Alusta offline-tallennusjärjestelmä"""
    
    def save_receipt(self, receipt: Receipt) -> bool:
        """Tallenna kuitti"""
    
    def load_receipt(self, filename: str) -> Optional[Receipt]:
        """Lataa kuitti tiedostosta"""
    
    def load_history(self) -> List[Dict]:
        """Lataa kuittihistoria"""
    
    def list_receipts(self) -> List[str]:
        """Listaa kaikki tallennetut kuitit"""
    
    def delete_receipt(self, filename: str) -> bool:
        """Poista kuitti"""
```

### Receipt

```python
class Receipt:
    def set_custom_logo(self, text: str, style: str = "box"):
        """Aseta mukautettu logo"""
    
    def set_payment_info(
        self, 
        method: str, 
        card_type: str = "", 
        transaction_id: str = "", 
        bank_reference: str = ""
    ):
        """Aseta maksutiedot"""
    
    def update_company_info(self, **kwargs):
        """Päivitä yritystiedot"""
    
    def to_dict(self) -> Dict:
        """Muunna sanakirjaksi"""
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Luo kuitti sanakirjasta"""
```

## 📊 Testaus / Testing

Suorita demo nähdäksesi kaikki ominaisuudet toiminnassa:

```bash
python demo_kuittikone_features.py
```

Demo näyttää:
1. ASCII-logon generoinnin eri tyyleillä
2. Maksutietojen lisäyksen
3. Mukautetun logon käytön
4. Offline-tallennuksen
5. Yritystietojen muokkauksen

## 🌐 Monikielisyys / Multilingual Support

Sovellus tukee suomea ja englantia:
- Kaikki käyttöliittymätekstit suomeksi ja englanniksi
- Kuitit suomeksi oletuksena
- Helppo laajentaa muille kielille

## 🔒 Turvallisuus / Security

- Offline-toiminta - ei verkkoyhteyttä tarvita
- Paikalliset tiedostot - data ei lähde koneelta
- JSON-tallennusmuoto - helppo tarkistaa ja varmuuskopioida
- Ei salasanoja tai arkaluonteisia tietoja tallenneta oletuksena

## 🐛 Vianmääritys / Troubleshooting

### Tkinter ei toimi / Tkinter not working
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (Homebrew)
brew install python-tk

# Käytä terminaalitilaa
python receipt_app.py --terminal
```

### Pillow-virhe / Pillow error
```bash
pip install pillow
```

### Tallennusoikeudet / Storage permissions
Varmista että sovelluksella on kirjoitusoikeudet:
```bash
chmod +w kuitit_offline/
```

## 📝 Lisenssi / License

Katso LICENSE-tiedosto / See LICENSE file

## 👨‍💻 Kehittäjät / Developers

- AnomFIN
- HRK Team

## 🔄 Versiohistoria / Version History

### v2.0.0 (2024-11-22)
- ✨ ASCII-logon generointi
- 💳 Maksutietojen hallinta
- 💾 Offline-tallennus
- ⚙️ Muokattavat asetukset
- 📋 Kuittihistoria
- 📝 Lisähuomiot
- 🔄 Vienti/tuonti

### v1.0.0
- Peruskuittitoiminnallisuus
- GUI ja terminaalitila
- PNG-tallennus

## 🤝 Osallistuminen / Contributing

Tervetuloa osallistumaan kehitykseen! / Welcome to contribute!

1. Fork repositorio
2. Luo feature-branch (`git checkout -b feature/AmazingFeature`)
3. Commit muutokset (`git commit -m 'Add amazing feature'`)
4. Push branchiin (`git push origin feature/AmazingFeature`)
5. Avaa Pull Request

## 📞 Tuki / Support

Ongelmatilanteissa avaa issue GitHubissa / For issues, open an issue on GitHub

---

**Kiitos käytöstä! / Thank you for using Kuittikone!** 🎉
