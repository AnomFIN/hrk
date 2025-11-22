#!/usr/bin/env python3
"""
Kuittitulostin - Receipt Printer Application
Harjun Raskaskone Oy (HRK)

Yhden tiedoston kuittisovellus GUI:lla ja terminaalituella.
Single-file receipt application with GUI and terminal support.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Yritä tuoda GUI-kirjastot / Try to import GUI libraries
GUI_AVAILABLE = False
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, simpledialog
    GUI_AVAILABLE = True
except ImportError:
    pass

# Yritä tuoda Pillow kuvien käsittelyyn / Try to import Pillow for image handling
PILLOW_AVAILABLE = False
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    pass

# Colorama terminaalin väreihin / Colorama for terminal colors
COLORAMA_AVAILABLE = False
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    pass


class Product:
    """Tuote-olio / Product object"""
    def __init__(self, name: str, quantity: int, price: float):
        self.name = name
        self.quantity = quantity
        self.price = price
    
    def total(self) -> float:
        """Tuotteen kokonaishinta / Product total price"""
        return self.quantity * self.price
    
    def to_dict(self) -> Dict:
        """Muunna sanakirjaksi / Convert to dictionary"""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price
        }


class ASCIILogoGenerator:
    """ASCII-logon generaattori / ASCII logo generator"""
    
    @staticmethod
    def generate(text: str, style: str = "box") -> str:
        """
        Generoi ASCII-logo eri tyyleillä / Generate ASCII logo with different styles
        
        Tyylit / Styles:
        - box: laatikkoreunukset / box borders
        - stars: tähtireunukset / star borders
        - double: kaksoisviiva / double line
        - simple: yksinkertainen / simple
        - banner: banneri / banner style
        - fancy: koristeellinen / fancy decorative
        - shadow: varjostus / shadow effect
        - blocks: lohkokirjaimet / block letters
        - wave: aaltoviiva / wave pattern
        - diamond: timantti / diamond pattern
        """
        if style == "box":
            width = len(text) + 6
            top = "╔" + "═" * (width - 2) + "╗"
            middle = f"║  {text.upper()}  ║"
            bottom = "╚" + "═" * (width - 2) + "╝"
            return f"{top}\n{middle}\n{bottom}"
        
        elif style == "stars":
            width = len(text) + 6
            top = "✦" + "·" * (width - 2) + "✦"
            middle = f"✦  {text.upper()}  ✦"
            bottom = "✦" + "·" * (width - 2) + "✦"
            return f"{top}\n{middle}\n{bottom}"
        
        elif style == "double":
            width = len(text) + 8
            top = "╔" + "═" * (width - 2) + "╗"
            top2 = "║" + " " * (width - 2) + "║"
            middle = f"║   {text.upper()}   ║"
            bottom2 = "║" + " " * (width - 2) + "║"
            bottom = "╚" + "═" * (width - 2) + "╝"
            return f"{top}\n{top2}\n{middle}\n{bottom2}\n{bottom}"
        
        elif style == "banner":
            width = len(text) + 8
            top = "╭" + "─" * (width - 2) + "╮"
            middle = f"│   {text.upper()}   │"
            bottom = "╰" + "─" * (width - 2) + "╯"
            return f"{top}\n{middle}\n{bottom}"
        
        elif style == "fancy":
            width = len(text) + 8
            # Create decorative double-line border
            top = "╔" + "═" * (width - 2) + "╗"
            top2 = "║" + "·" * (width - 2) + "║"
            middle = f"║   {text.upper()}   ║"
            bottom2 = "║" + "·" * (width - 2) + "║"
            bottom = "╚" + "═" * (width - 2) + "╝"
            return f"{top}\n{top2}\n{middle}\n{bottom2}\n{bottom}"
        
        elif style == "shadow":
            width = len(text) + 6
            top = "┌" + "─" * (width - 2) + "┐"
            middle = f"│  {text.upper()}  │▓"
            bottom = "└" + "─" * (width - 2) + "┘▓"
            shadow = " " + "▓" * (width - 1)
            return f"{top}\n{middle}\n{bottom}\n{shadow}"
        
        elif style == "blocks":
            # Create stylized block representation
            text_upper = text.upper()
            width = len(text_upper) + 8
            
            # Create border and text with block styling
            top = "╔" + "═" * (width - 2) + "╗"
            middle1 = f"║   {text_upper}   ║"
            # Add block underline effect
            blocks = "▓" * len(text_upper)
            middle2 = f"║   {blocks}   ║"
            bottom = "╚" + "═" * (width - 2) + "╝"
            
            return f"{top}\n{middle1}\n{middle2}\n{bottom}"
        
        elif style == "wave":
            width = len(text) + 8
            top = "～" * width
            middle = f"～  {text.upper()}  ～"
            bottom = "～" * width
            return f"{top}\n{middle}\n{bottom}"
        
        elif style == "diamond":
            width = len(text) + 8
            top = "◆" + "─" * (width - 2) + "◆"
            middle = f"│  {text.upper()}  │"
            bottom = "◆" + "─" * (width - 2) + "◆"
            return f"{top}\n{middle}\n{bottom}"
        
        else:  # simple
            border = "=" * (len(text) + 4)
            middle = f"  {text.upper()}  "
            return f"{border}\n{middle}\n{border}"


class Receipt:
    """Kuitti-olio / Receipt object"""
    
    # ASCII-logo yritykselle / ASCII logo for company
    LOGO = """
    ╔═══════════════════════════════════════╗
    ║   HARJUN RASKASKONE OY (HRK)          ║
    ║   Laadukasta laitevuokrausta          ║
    ╚═══════════════════════════════════════╝
    """
    
    VAT_RATE = 0.24  # ALV 24%
    
    def __init__(self):
        self.products: List[Product] = []
        self.company_info = {
            "name": "Harjun Raskaskone Oy",
            "business_id": "FI12345678",
            "address": "Teollisuustie 1, 00100 Helsinki",
            "phone": "+358 40 123 4567",
            "email": "info@hrk.fi",
            "website": "www.hrk.fi"
        }
        self.payment_info = {
            "method": "Käteinen / Cash",
            "card_type": "",
            "transaction_id": "",
            "bank_reference": ""
        }
        self.custom_logo = None
        self.logo_style = "box"
        self.receipt_notes = ""
    
    def add_product(self, name: str, quantity: int, price: float) -> bool:
        """Lisää tuote / Add product"""
        try:
            if quantity <= 0 or price < 0:
                return False
            self.products.append(Product(name, quantity, price))
            return True
        except Exception:
            return False
    
    def remove_product(self, index: int) -> bool:
        """Poista tuote / Remove product"""
        try:
            if 0 <= index < len(self.products):
                self.products.pop(index)
                return True
            return False
        except Exception:
            return False
    
    def get_subtotal(self) -> float:
        """Välisumma ilman ALV:ia / Subtotal without VAT"""
        return sum(p.total() for p in self.products)
    
    def get_vat(self) -> float:
        """ALV-summa / VAT amount"""
        return self.get_subtotal() * self.VAT_RATE
    
    def get_total(self) -> float:
        """Kokonaissumma sisältäen ALV:in / Total including VAT"""
        return self.get_subtotal() + self.get_vat()
    
    def set_custom_logo(self, text: str, style: str = "box"):
        """Aseta mukautettu logo / Set custom logo"""
        self.custom_logo = ASCIILogoGenerator.generate(text, style)
        self.logo_style = style
    
    def set_payment_info(self, method: str, card_type: str = "", transaction_id: str = "", bank_reference: str = ""):
        """Aseta maksutiedot / Set payment information"""
        self.payment_info = {
            "method": method,
            "card_type": card_type,
            "transaction_id": transaction_id,
            "bank_reference": bank_reference
        }
    
    def update_company_info(self, **kwargs):
        """Päivitä yritystiedot / Update company information"""
        self.company_info.update(kwargs)
    
    def generate_text(self) -> str:
        """Luo tekstimuotoinen kuitti / Generate text receipt"""
        lines = []
        
        # Logo
        if self.custom_logo:
            lines.append(self.custom_logo)
        else:
            lines.append(self.LOGO)
        
        # Yritystiedot / Company info
        lines.append(f"\n{self.company_info['name']}")
        lines.append(f"Y-tunnus: {self.company_info['business_id']}")
        lines.append(f"{self.company_info['address']}")
        lines.append(f"Puh: {self.company_info['phone']}")
        if self.company_info.get('email'):
            lines.append(f"Email: {self.company_info['email']}")
        if self.company_info.get('website'):
            lines.append(f"Web: {self.company_info['website']}")
        
        lines.append(f"\nPäivämäärä: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        lines.append("\n" + "=" * 50)
        lines.append("\nTUOTTEET / PRODUCTS:")
        lines.append("-" * 50)
        
        for i, product in enumerate(self.products, 1):
            lines.append(f"{i}. {product.name}")
            lines.append(f"   {product.quantity} kpl x {product.price:.2f} € = {product.total():.2f} €")
        
        lines.append("-" * 50)
        lines.append(f"Välisumma (ilman ALV): {self.get_subtotal():.2f} €")
        lines.append(f"ALV 24%: {self.get_vat():.2f} €")
        lines.append("=" * 50)
        lines.append(f"YHTEENSÄ: {self.get_total():.2f} €")
        lines.append("=" * 50)
        
        # Maksutiedot / Payment information
        lines.append(f"\nMaksutapa / Payment method: {self.payment_info['method']}")
        if self.payment_info['card_type']:
            lines.append(f"Korttityyppi / Card type: {self.payment_info['card_type']}")
        if self.payment_info['transaction_id']:
            lines.append(f"Tapahtumatunnus / Transaction ID: {self.payment_info['transaction_id']}")
        if self.payment_info['bank_reference']:
            lines.append(f"Viite / Reference: {self.payment_info['bank_reference']}")
        
        # Lisähuomiot / Additional notes
        if self.receipt_notes:
            lines.append(f"\nHuomiot / Notes:\n{self.receipt_notes}")
        
        lines.append("\nKiitos ostoksesta! / Thank you for your purchase!")
        lines.append("\n")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Muunna sanakirjaksi tallennusta varten / Convert to dictionary for saving"""
        return {
            "timestamp": datetime.now().isoformat(),
            "company_info": self.company_info,
            "payment_info": self.payment_info,
            "products": [p.to_dict() for p in self.products],
            "subtotal": self.get_subtotal(),
            "vat": self.get_vat(),
            "total": self.get_total(),
            "custom_logo": self.custom_logo,
            "logo_style": self.logo_style,
            "receipt_notes": self.receipt_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Luo kuitti sanakirjasta / Create receipt from dictionary"""
        receipt = cls()
        receipt.company_info = data.get("company_info", receipt.company_info)
        receipt.payment_info = data.get("payment_info", receipt.payment_info)
        receipt.custom_logo = data.get("custom_logo")
        receipt.logo_style = data.get("logo_style", "box")
        receipt.receipt_notes = data.get("receipt_notes", "")
        
        for product_data in data.get("products", []):
            receipt.add_product(
                product_data["name"],
                product_data["quantity"],
                product_data["price"]
            )
        
        return receipt


class OfflineStorage:
    """Offline-tallennusjärjestelmä / Offline storage system"""
    
    def __init__(self, storage_dir: str = "kuitit_offline"):
        """Alusta tallennuskansio / Initialize storage directory"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.history_file = self.storage_dir / "kuitti_historia.json"
        self.ensure_history_file()
    
    def ensure_history_file(self):
        """Varmista että historian tiedosto on olemassa / Ensure history file exists"""
        if not self.history_file.exists():
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def save_receipt(self, receipt: Receipt) -> bool:
        """
        Tallenna kuitti offline-tilaan / Save receipt to offline storage
        Returns: True jos onnistui / True if successful
        """
        try:
            # Luo aikaleimapohjainen tiedostonimi
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kuitti_{timestamp}.json"
            filepath = self.storage_dir / filename
            
            # Tallenna kuitti
            receipt_data = receipt.to_dict()
            receipt_data["filename"] = filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(receipt_data, f, indent=2, ensure_ascii=False)
            
            # Lisää historiaan
            self._add_to_history(receipt_data)
            
            # Tallenna myös tekstimuotoisena
            text_filepath = self.storage_dir / f"kuitti_{timestamp}.txt"
            with open(text_filepath, 'w', encoding='utf-8') as f:
                f.write(receipt.generate_text())
            
            return True
        except Exception as e:
            print(f"Tallennusvirhe / Save error: {e}")
            return False
    
    def _add_to_history(self, receipt_data: Dict):
        """Lisää kuitti historiaan / Add receipt to history"""
        try:
            history = self.load_history()
            history.append({
                "timestamp": receipt_data["timestamp"],
                "filename": receipt_data["filename"],
                "total": receipt_data["total"],
                "company": receipt_data["company_info"]["name"],
                "payment_method": receipt_data["payment_info"]["method"]
            })
            
            # Pidä vain viimeisimmät 100 kuittia historiassa
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Historian päivitysvirhe / History update error: {e}")
    
    def load_history(self) -> List[Dict]:
        """Lataa kuittihistoria / Load receipt history"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def load_receipt(self, filename: str) -> Optional[Receipt]:
        """Lataa kuitti tiedostosta / Load receipt from file"""
        try:
            filepath = self.storage_dir / filename
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Receipt.from_dict(data)
        except Exception as e:
            print(f"Latausvirhe / Load error: {e}")
            return None
    
    def list_receipts(self) -> List[str]:
        """Listaa kaikki tallennetut kuitit / List all saved receipts"""
        try:
            return [f.name for f in self.storage_dir.glob("kuitti_*.json")]
        except Exception:
            return []
    
    def delete_receipt(self, filename: str) -> bool:
        """Poista kuitti / Delete receipt"""
        try:
            json_path = self.storage_dir / filename
            txt_path = self.storage_dir / filename.replace('.json', '.txt')
            
            if json_path.exists():
                json_path.unlink()
            if txt_path.exists():
                txt_path.unlink()
            
            return True
        except Exception as e:
            print(f"Poistovirhe / Delete error: {e}")
            return False


class TemplateManager:
    """Kuittipohjan hallintajärjestelmä / Receipt template management system"""
    
    def __init__(self, templates_dir: str = "kuitti_pohjat"):
        """Alusta pohjakansio / Initialize templates directory"""
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
    
    def save_template(self, receipt: Receipt, template_name: str) -> bool:
        """
        Tallenna kuittipohja / Save receipt template
        
        Tallentaa kuitin asetukset (yritystiedot, maksutiedot, logo, huomiot)
        ilman tuotteita, jotta pohjaa voi käyttää uudelleen.
        
        Saves receipt settings (company info, payment info, logo, notes)
        without products, so template can be reused.
        """
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            
            # Luo pohja ilman tuotteita / Create template without products
            template_data = {
                "template_name": template_name,
                "created": datetime.now().isoformat(),
                "company_info": receipt.company_info,
                "payment_info": receipt.payment_info,
                "custom_logo": receipt.custom_logo,
                "logo_style": receipt.logo_style,
                "receipt_notes": receipt.receipt_notes
            }
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Pohjan tallennusvirhe / Template save error: {e}")
            return False
    
    def load_template(self, template_name: str) -> Optional[Receipt]:
        """
        Lataa kuittipohja / Load receipt template
        
        Lataa pohjan asetukset ja luo uuden tyhjän kuitin näillä asetuksilla.
        Loads template settings and creates new empty receipt with these settings.
        """
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            
            if not template_file.exists():
                print(f"Pohjaa ei löydy / Template not found: {template_name}")
                return None
            
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Luo uusi kuitti pohjasta / Create new receipt from template
            receipt = Receipt()
            receipt.company_info = template_data.get("company_info", receipt.company_info)
            receipt.payment_info = template_data.get("payment_info", receipt.payment_info)
            receipt.custom_logo = template_data.get("custom_logo")
            receipt.logo_style = template_data.get("logo_style", "box")
            receipt.receipt_notes = template_data.get("receipt_notes", "")
            
            return receipt
        except Exception as e:
            print(f"Pohjan latausvirhe / Template load error: {e}")
            return None
    
    def list_templates(self) -> List[str]:
        """Listaa kaikki tallennetut pohjat / List all saved templates"""
        try:
            templates = []
            for file in self.templates_dir.glob("*.json"):
                templates.append(file.stem)
            return sorted(templates)
        except Exception:
            return []
    
    def delete_template(self, template_name: str) -> bool:
        """Poista pohja / Delete template"""
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            if template_file.exists():
                template_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Pohjan poistovirhe / Template delete error: {e}")
            return False
    
    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """Hae pohjan tiedot / Get template information"""
        try:
            template_file = self.templates_dir / f"{template_name}.json"
            
            if not template_file.exists():
                return None
            
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None


class ReceiptPrinter:
    """Kuitin tulostus / Receipt printing"""
    
    @staticmethod
    def print_to_printer(text: str) -> bool:
        """Tulosta oletustulostimeen / Print to default printer"""
        try:
            system = platform.system()
            
            # Luo väliaikainen tiedosto / Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(text)
                temp_path = f.name
            
            try:
                if system == "Windows":
                    # Windows: käytä notepad /p komentoa
                    subprocess.run(["notepad", "/p", temp_path], check=True)
                    return True
                elif system == "Linux":
                    # Linux: yritä lpr-komentoa
                    result = subprocess.run(["lpr", temp_path], check=True)
                    return result.returncode == 0
                elif system == "Darwin":  # macOS
                    subprocess.run(["lpr", temp_path], check=True)
                    return True
                else:
                    return False
            finally:
                # Poista väliaikainen tiedosto / Remove temporary file
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"Tulostusvirhe / Print error: {e}")
            return False
    
    @staticmethod
    def save_as_png(text: str, filepath: str) -> bool:
        """Tallenna kuitti PNG-kuvana / Save receipt as PNG"""
        if not PILLOW_AVAILABLE:
            print("Pillow-kirjasto puuttuu! / Pillow library missing!")
            return False
        
        try:
            # Kuvan asetukset / Image settings
            line_height = 20
            padding = 30
            font_size = 14
            
            lines = text.split('\n')
            
            # Käytä monospace-fonttia jos mahdollista / Use monospace font if possible
            try:
                font = ImageFont.truetype("cour.ttf", font_size)  # Courier New (Windows)
            except Exception:
                try:
                    font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)  # Linux
                except Exception:
                    font = ImageFont.load_default()
            
            # Laske kuvan koko / Calculate image size
            max_width = 0
            for line in lines:
                try:
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]
                except Exception:
                    line_width = len(line) * 10  # Arvio / Estimate
                max_width = max(max_width, line_width)
            
            width = max_width + (2 * padding)
            height = (len(lines) * line_height) + (2 * padding)
            
            # Luo kuva / Create image
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Piirrä teksti / Draw text
            y = padding
            for line in lines:
                draw.text((padding, y), line, fill='black', font=font)
                y += line_height
            
            # Tallenna / Save
            img.save(filepath)
            return True
            
        except Exception as e:
            print(f"PNG-tallennus epäonnistui / PNG save failed: {e}")
            return False


class ReceiptAppGUI:
    """GUI-sovellus Tkinterillä / GUI application with Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Kuittitulostin - HRK Receipt Printer")
        self.root.geometry("900x700")
        
        self.receipt = Receipt()
        self.storage = OfflineStorage()
        self.template_manager = TemplateManager()
        
        # Keskiosa: tuotelista / Center: product list
        self.create_widgets()
        
        # Päivitä näyttö / Update display
        self.update_display()
    
    def create_widgets(self):
        """Luo GUI-elementit / Create GUI elements"""
        
        # Otsikko / Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", padx=10, pady=10)
        title_frame.pack(fill=tk.X)
        
        title = tk.Label(
            title_frame, 
            text="KUITTITULOSTIN - HRK RECEIPT PRINTER",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack()
        
        # Tuotteen lisäys / Product entry
        entry_frame = tk.Frame(self.root, padx=10, pady=10)
        entry_frame.pack(fill=tk.X)
        
        tk.Label(entry_frame, text="Tuotenimi / Product:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(entry_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(entry_frame, text="Määrä / Quantity:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.qty_entry = tk.Entry(entry_frame, width=10)
        self.qty_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(entry_frame, text="Hinta / Price (€):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.price_entry = tk.Entry(entry_frame, width=15)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)
        
        btn_add = tk.Button(
            entry_frame,
            text="Lisää tuote / Add Product",
            command=self.add_product,
            bg="#27ae60",
            fg="white",
            padx=10,
            pady=5
        )
        btn_add.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        # Tuotelista / Product list
        list_frame = tk.Frame(self.root, padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Ostoskori / Shopping Cart:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Treeview tuotteille / Treeview for products
        columns = ("Tuote", "Määrä", "Hinta", "Yhteensä")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Poistopainike / Remove button
        btn_remove = tk.Button(
            list_frame,
            text="Poista valittu / Remove Selected",
            command=self.remove_product,
            bg="#e74c3c",
            fg="white",
            padx=10,
            pady=5
        )
        btn_remove.pack(pady=5)
        
        # Yhteenveto / Summary
        summary_frame = tk.Frame(self.root, padx=10, pady=10, bg="#ecf0f1")
        summary_frame.pack(fill=tk.X)
        
        self.subtotal_label = tk.Label(summary_frame, text="Välisumma: 0.00 €", font=("Arial", 11), bg="#ecf0f1")
        self.subtotal_label.pack(anchor=tk.E)
        
        self.vat_label = tk.Label(summary_frame, text="ALV 24%: 0.00 €", font=("Arial", 11), bg="#ecf0f1")
        self.vat_label.pack(anchor=tk.E)
        
        self.total_label = tk.Label(summary_frame, text="YHTEENSÄ: 0.00 €", font=("Arial", 14, "bold"), bg="#ecf0f1")
        self.total_label.pack(anchor=tk.E)
        
        # Toimintopainikkeet / Action buttons
        button_frame = tk.Frame(self.root, padx=10, pady=10)
        button_frame.pack(fill=tk.X)
        
        btn_print = tk.Button(
            button_frame,
            text="Tulosta kuitti / Print Receipt",
            command=self.print_receipt,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8
        )
        btn_print.pack(side=tk.LEFT, padx=5)
        
        btn_save = tk.Button(
            button_frame,
            text="Tallenna PNG / Save PNG",
            command=self.save_png,
            bg="#9b59b6",
            fg="white",
            padx=15,
            pady=8
        )
        btn_save.pack(side=tk.LEFT, padx=5)
        
        btn_save_offline = tk.Button(
            button_frame,
            text="💾 Tallenna offline",
            command=self.save_offline,
            bg="#16a085",
            fg="white",
            padx=15,
            pady=8
        )
        btn_save_offline.pack(side=tk.LEFT, padx=5)
        
        btn_settings = tk.Button(
            button_frame,
            text="⚙️ Asetukset",
            command=self.show_settings,
            bg="#f39c12",
            fg="white",
            padx=15,
            pady=8
        )
        btn_settings.pack(side=tk.LEFT, padx=5)
        
        btn_history = tk.Button(
            button_frame,
            text="📋 Historia",
            command=self.show_history,
            bg="#8e44ad",
            fg="white",
            padx=15,
            pady=8
        )
        btn_history.pack(side=tk.LEFT, padx=5)
        
        btn_save_template = tk.Button(
            button_frame,
            text="📝 Tallenna pohja",
            command=self.save_template,
            bg="#1abc9c",
            fg="white",
            padx=15,
            pady=8
        )
        btn_save_template.pack(side=tk.LEFT, padx=5)
        
        btn_load_template = tk.Button(
            button_frame,
            text="📂 Lataa pohja",
            command=self.load_template,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8
        )
        btn_load_template.pack(side=tk.LEFT, padx=5)
        
        btn_clear = tk.Button(
            button_frame,
            text="Tyhjennä / Clear",
            command=self.clear_receipt,
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=8
        )
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        btn_exit = tk.Button(
            button_frame,
            text="Lopeta / Exit",
            command=self.exit_app,
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=8
        )
        btn_exit.pack(side=tk.RIGHT, padx=5)
    
    def add_product(self):
        """Lisää tuote ostoskoriin / Add product to cart"""
        try:
            name = self.name_entry.get().strip()
            qty_str = self.qty_entry.get().strip()
            price_str = self.price_entry.get().strip()
            
            if not name or not qty_str or not price_str:
                messagebox.showwarning("Virhe", "Täytä kaikki kentät! / Fill all fields!")
                return
            
            quantity = int(qty_str)
            price = float(price_str)
            
            if self.receipt.add_product(name, quantity, price):
                # Tyhjennä kentät / Clear fields
                self.name_entry.delete(0, tk.END)
                self.qty_entry.delete(0, tk.END)
                self.price_entry.delete(0, tk.END)
                
                self.update_display()
            else:
                messagebox.showerror("Virhe", "Virheelliset arvot! / Invalid values!")
                
        except ValueError:
            messagebox.showerror("Virhe", "Tarkista määrä ja hinta! / Check quantity and price!")
    
    def remove_product(self):
        """Poista valittu tuote / Remove selected product"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Virhe", "Valitse poistettava tuote! / Select product to remove!")
            return
        
        # Hae indeksi / Get index
        item = selected[0]
        index = self.tree.index(item)
        
        if self.receipt.remove_product(index):
            self.update_display()
    
    def update_display(self):
        """Päivitä näyttö / Update display"""
        # Tyhjennä lista / Clear list
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lisää tuotteet / Add products
        for product in self.receipt.products:
            self.tree.insert("", tk.END, values=(
                product.name,
                product.quantity,
                f"{product.price:.2f} €",
                f"{product.total():.2f} €"
            ))
        
        # Päivitä yhteenveto / Update summary
        self.subtotal_label.config(text=f"Välisumma: {self.receipt.get_subtotal():.2f} €")
        self.vat_label.config(text=f"ALV 24%: {self.receipt.get_vat():.2f} €")
        self.total_label.config(text=f"YHTEENSÄ: {self.receipt.get_total():.2f} €")
    
    def print_receipt(self):
        """Tulosta kuitti / Print receipt"""
        if not self.receipt.products:
            messagebox.showwarning("Virhe", "Lisää tuotteita ensin! / Add products first!")
            return
        
        text = self.receipt.generate_text()
        if ReceiptPrinter.print_to_printer(text):
            messagebox.showinfo("Onnistui", "Kuitti lähetetty tulostimeen! / Receipt sent to printer!")
        else:
            messagebox.showerror("Virhe", "Tulostus epäonnistui! / Print failed!")
    
    def save_png(self):
        """Tallenna kuitti PNG:ksi / Save receipt as PNG"""
        if not self.receipt.products:
            messagebox.showwarning("Virhe", "Lisää tuotteita ensin! / Add products first!")
            return
        
        if not PILLOW_AVAILABLE:
            messagebox.showerror("Virhe", "Pillow-kirjasto puuttuu! Asenna: pip install pillow\nPillow library missing! Install: pip install pillow")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"kuitti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        if filepath:
            text = self.receipt.generate_text()
            if ReceiptPrinter.save_as_png(text, filepath):
                messagebox.showinfo("Onnistui", f"Kuitti tallennettu: {filepath}\nReceipt saved: {filepath}")
            else:
                messagebox.showerror("Virhe", "Tallennus epäonnistui! / Save failed!")
    
    def clear_receipt(self):
        """Tyhjennä kuitti / Clear receipt"""
        if self.receipt.products:
            if messagebox.askyesno("Vahvista", "Tyhjennetäänkö ostoskori? / Clear shopping cart?"):
                self.receipt.products.clear()
                self.update_display()
    
    def save_offline(self):
        """Tallenna kuitti offline-tilaan / Save receipt offline"""
        if not self.receipt.products:
            messagebox.showwarning("Virhe", "Lisää tuotteita ensin! / Add products first!")
            return
        
        if self.storage.save_receipt(self.receipt):
            messagebox.showinfo(
                "Onnistui",
                f"Kuitti tallennettu offline-tilaan!\nReceipt saved offline!\nKansio: {self.storage.storage_dir}"
            )
        else:
            messagebox.showerror("Virhe", "Offline-tallennus epäonnistui! / Offline save failed!")
    
    def show_settings(self):
        """Näytä asetusten / Show settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Asetukset / Settings")
        settings_window.geometry("600x600")
        
        # Notebook (tabs)
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Yritystiedot / Company info
        company_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(company_frame, text="Yritystiedot / Company")
        
        tk.Label(company_frame, text="Yrityksen nimi / Company name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        company_name_entry = tk.Entry(company_frame, width=40)
        company_name_entry.insert(0, self.receipt.company_info['name'])
        company_name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(company_frame, text="Y-tunnus / Business ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        business_id_entry = tk.Entry(company_frame, width=40)
        business_id_entry.insert(0, self.receipt.company_info['business_id'])
        business_id_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(company_frame, text="Osoite / Address:").grid(row=2, column=0, sticky=tk.W, pady=5)
        address_entry = tk.Entry(company_frame, width=40)
        address_entry.insert(0, self.receipt.company_info['address'])
        address_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(company_frame, text="Puhelin / Phone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        phone_entry = tk.Entry(company_frame, width=40)
        phone_entry.insert(0, self.receipt.company_info['phone'])
        phone_entry.grid(row=3, column=1, pady=5)
        
        tk.Label(company_frame, text="Sähköposti / Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        email_entry = tk.Entry(company_frame, width=40)
        email_entry.insert(0, self.receipt.company_info.get('email', ''))
        email_entry.grid(row=4, column=1, pady=5)
        
        tk.Label(company_frame, text="Verkkosivu / Website:").grid(row=5, column=0, sticky=tk.W, pady=5)
        website_entry = tk.Entry(company_frame, width=40)
        website_entry.insert(0, self.receipt.company_info.get('website', ''))
        website_entry.grid(row=5, column=1, pady=5)
        
        # Tab 2: Maksutiedot / Payment info
        payment_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(payment_frame, text="Maksutiedot / Payment")
        
        tk.Label(payment_frame, text="Maksutapa / Payment method:").grid(row=0, column=0, sticky=tk.W, pady=5)
        payment_method_var = tk.StringVar(value=self.receipt.payment_info['method'])
        payment_methods = ["Käteinen / Cash", "Kortti / Card", "Lasku / Invoice", "Verkkopankki / Online banking"]
        payment_method_combo = ttk.Combobox(payment_frame, textvariable=payment_method_var, values=payment_methods, width=37)
        payment_method_combo.grid(row=0, column=1, pady=5)
        
        tk.Label(payment_frame, text="Korttityyppi / Card type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        card_type_entry = tk.Entry(payment_frame, width=40)
        card_type_entry.insert(0, self.receipt.payment_info.get('card_type', ''))
        card_type_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(payment_frame, text="Tapahtumatunnus / Transaction ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        transaction_id_entry = tk.Entry(payment_frame, width=40)
        transaction_id_entry.insert(0, self.receipt.payment_info.get('transaction_id', ''))
        transaction_id_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(payment_frame, text="Pankkiviite / Bank reference:").grid(row=3, column=0, sticky=tk.W, pady=5)
        bank_ref_entry = tk.Entry(payment_frame, width=40)
        bank_ref_entry.insert(0, self.receipt.payment_info.get('bank_reference', ''))
        bank_ref_entry.grid(row=3, column=1, pady=5)
        
        # Tab 3: ASCII Logo
        logo_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(logo_frame, text="ASCII Logo")
        
        tk.Label(logo_frame, text="Logo-teksti / Logo text:").grid(row=0, column=0, sticky=tk.W, pady=5)
        logo_text_entry = tk.Entry(logo_frame, width=40)
        logo_text_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(logo_frame, text="Tyyli / Style:").grid(row=1, column=0, sticky=tk.W, pady=5)
        logo_style_var = tk.StringVar(value=self.receipt.logo_style)
        logo_styles = ["box", "stars", "double", "simple", "banner", "fancy", "shadow", "blocks", "wave", "diamond"]
        logo_style_combo = ttk.Combobox(logo_frame, textvariable=logo_style_var, values=logo_styles, width=37)
        logo_style_combo.grid(row=1, column=1, pady=5)
        
        tk.Label(logo_frame, text="Esikatselu / Preview:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        logo_preview_text = tk.Text(logo_frame, width=50, height=10, font=("Courier", 10))
        logo_preview_text.grid(row=2, column=1, pady=5)
        
        def update_logo_preview():
            text = logo_text_entry.get().strip()
            if text:
                style = logo_style_var.get()
                preview = ASCIILogoGenerator.generate(text, style)
                logo_preview_text.delete(1.0, tk.END)
                logo_preview_text.insert(1.0, preview)
        
        btn_preview_logo = tk.Button(logo_frame, text="Päivitä esikatselu / Update preview", command=update_logo_preview)
        btn_preview_logo.grid(row=3, column=1, pady=5)
        
        # Tab 4: Lisähuomiot / Notes
        notes_frame = tk.Frame(notebook, padx=20, pady=20)
        notebook.add(notes_frame, text="Huomiot / Notes")
        
        tk.Label(notes_frame, text="Kuitin lisähuomiot / Receipt notes:").pack(anchor=tk.W, pady=5)
        notes_text = tk.Text(notes_frame, width=60, height=15)
        notes_text.insert(1.0, self.receipt.receipt_notes)
        notes_text.pack(pady=5)
        
        # Tallennuspainike / Save button
        def save_settings():
            # Yritystiedot
            self.receipt.update_company_info(
                name=company_name_entry.get(),
                business_id=business_id_entry.get(),
                address=address_entry.get(),
                phone=phone_entry.get(),
                email=email_entry.get(),
                website=website_entry.get()
            )
            
            # Maksutiedot
            self.receipt.set_payment_info(
                method=payment_method_var.get(),
                card_type=card_type_entry.get(),
                transaction_id=transaction_id_entry.get(),
                bank_reference=bank_ref_entry.get()
            )
            
            # Logo
            logo_text = logo_text_entry.get().strip()
            if logo_text:
                self.receipt.set_custom_logo(logo_text, logo_style_var.get())
            
            # Huomiot
            self.receipt.receipt_notes = notes_text.get(1.0, tk.END).strip()
            
            messagebox.showinfo("Tallennettu", "Asetukset tallennettu! / Settings saved!")
            settings_window.destroy()
        
        save_button = tk.Button(settings_window, text="Tallenna / Save", command=save_settings, bg="#27ae60", fg="white", padx=20, pady=10)
        save_button.pack(pady=10)
    
    def show_history(self):
        """Näytä kuittihistoria / Show receipt history"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Kuittihistoria / Receipt History")
        history_window.geometry("800x500")
        
        tk.Label(history_window, text="Tallennetut kuitit / Saved receipts", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Treeview historialle
        columns = ("Aika / Time", "Yritys / Company", "Summa / Total", "Maksutapa / Payment")
        tree = ttk.Treeview(history_window, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=190)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lataa historia
        history = self.storage.load_history()
        for entry in reversed(history):  # Näytä uusimmat ensin
            tree.insert("", tk.END, values=(
                entry.get("timestamp", ""),
                entry.get("company", ""),
                f"{entry.get('total', 0):.2f} €",
                entry.get("payment_method", "")
            ), tags=(entry.get("filename", ""),))
        
        # Toimintopainikkeet
        button_frame = tk.Frame(history_window)
        button_frame.pack(pady=10)
        
        def load_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Virhe", "Valitse kuitti! / Select receipt!")
                return
            
            item = tree.item(selected[0])
            filename = item['tags'][0]
            
            loaded_receipt = self.storage.load_receipt(filename)
            if loaded_receipt:
                self.receipt = loaded_receipt
                self.update_display()
                messagebox.showinfo("Ladattu", "Kuitti ladattu! / Receipt loaded!")
                history_window.destroy()
            else:
                messagebox.showerror("Virhe", "Lataus epäonnistui! / Load failed!")
        
        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Virhe", "Valitse kuitti! / Select receipt!")
                return
            
            if messagebox.askyesno("Vahvista", "Poistetaanko kuitti? / Delete receipt?"):
                item = tree.item(selected[0])
                filename = item['tags'][0]
                
                if self.storage.delete_receipt(filename):
                    tree.delete(selected[0])
                    messagebox.showinfo("Poistettu", "Kuitti poistettu! / Receipt deleted!")
                else:
                    messagebox.showerror("Virhe", "Poisto epäonnistui! / Delete failed!")
        
        tk.Button(button_frame, text="Lataa / Load", command=load_selected, bg="#3498db", fg="white", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Poista / Delete", command=delete_selected, bg="#e74c3c", fg="white", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sulje / Close", command=history_window.destroy, bg="#95a5a6", fg="white", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
    
    def save_template(self):
        """Tallenna kuittipohja / Save receipt template"""
        # Kysy pohjan nimi / Ask for template name
        template_name = tk.simpledialog.askstring(
            "Tallenna pohja / Save Template",
            "Anna pohjan nimi / Enter template name:",
            parent=self.root
        )
        
        if not template_name:
            return
        
        # Tallenna pohja / Save template
        if self.template_manager.save_template(self.receipt, template_name):
            messagebox.showinfo(
                "Tallennettu",
                f"Pohja '{template_name}' tallennettu!\nTemplate '{template_name}' saved!\n\n"
                f"Sisältää / Contains:\n"
                f"• Yritystiedot / Company info\n"
                f"• Maksutiedot / Payment info\n"
                f"• Logo-asetukset / Logo settings\n"
                f"• Huomiot / Notes"
            )
        else:
            messagebox.showerror("Virhe", "Pohjan tallennus epäonnistui! / Template save failed!")
    
    def load_template(self):
        """Lataa kuittipohja / Load receipt template"""
        # Hae lista pohjista / Get list of templates
        templates = self.template_manager.list_templates()
        
        if not templates:
            messagebox.showinfo(
                "Ei pohjia",
                "Ei tallennettuja pohjia!\nNo saved templates!\n\n"
                "Tallenna ensin pohja 📝 Tallenna pohja -painikkeella."
            )
            return
        
        # Näytä pohjan valintaikkuna / Show template selection dialog
        template_window = tk.Toplevel(self.root)
        template_window.title("Lataa pohja / Load Template")
        template_window.geometry("600x400")
        
        tk.Label(
            template_window,
            text="Valitse ladattava pohja / Select template to load",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        # Lista pohjista / List of templates
        listbox_frame = tk.Frame(template_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        template_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 11),
            height=10
        )
        template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=template_listbox.yview)
        
        # Lisää pohjat listaan / Add templates to list
        for template in templates:
            template_info = self.template_manager.get_template_info(template)
            if template_info:
                created = template_info.get("created", "")
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created)
                        created_str = created_dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        created_str = created
                else:
                    created_str = ""
                
                display_name = f"{template}  ({created_str})" if created_str else template
                template_listbox.insert(tk.END, display_name)
            else:
                template_listbox.insert(tk.END, template)
        
        # Esikatselu / Preview
        preview_frame = tk.Frame(template_window, padx=10, pady=10)
        preview_frame.pack(fill=tk.X)
        
        preview_label = tk.Label(preview_frame, text="", justify=tk.LEFT, font=("Arial", 9))
        preview_label.pack()
        
        def show_preview(event):
            selection = template_listbox.curselection()
            if selection:
                idx = selection[0]
                template_name = templates[idx]
                template_info = self.template_manager.get_template_info(template_name)
                
                if template_info:
                    company = template_info.get("company_info", {}).get("name", "N/A")
                    logo_style = template_info.get("logo_style", "N/A")
                    payment_method = template_info.get("payment_info", {}).get("method", "N/A")
                    
                    preview_text = (
                        f"Yritys / Company: {company}\n"
                        f"Logo-tyyli / Logo style: {logo_style}\n"
                        f"Maksutapa / Payment: {payment_method}"
                    )
                    preview_label.config(text=preview_text)
        
        template_listbox.bind('<<ListboxSelect>>', show_preview)
        
        # Painikkeet / Buttons
        button_frame = tk.Frame(template_window)
        button_frame.pack(pady=10)
        
        def load_selected():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Virhe", "Valitse pohja! / Select a template!")
                return
            
            idx = selection[0]
            template_name = templates[idx]
            
            # Lataa pohja / Load template
            loaded_receipt = self.template_manager.load_template(template_name)
            
            if loaded_receipt:
                # Säilytä nykyiset tuotteet jos halutaan / Keep current products if desired
                if self.receipt.products:
                    keep = messagebox.askyesno(
                        "Säilytä tuotteet?",
                        "Säilytetäänkö nykyiset tuotteet?\nKeep current products?"
                    )
                    if keep:
                        # Kopioi tuotteet uuteen kuittiin / Copy products to new receipt
                        for product in self.receipt.products:
                            loaded_receipt.add_product(product.name, product.quantity, product.price)
                
                self.receipt = loaded_receipt
                self.update_display()
                messagebox.showinfo("Ladattu", f"Pohja '{template_name}' ladattu! / Template loaded!")
                template_window.destroy()
            else:
                messagebox.showerror("Virhe", "Pohjan lataus epäonnistui! / Template load failed!")
        
        def delete_selected():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Virhe", "Valitse pohja! / Select a template!")
                return
            
            idx = selection[0]
            template_name = templates[idx]
            
            if messagebox.askyesno(
                "Vahvista poisto",
                f"Poistetaanko pohja '{template_name}'?\nDelete template '{template_name}'?"
            ):
                if self.template_manager.delete_template(template_name):
                    template_listbox.delete(idx)
                    templates.pop(idx)
                    preview_label.config(text="")
                    messagebox.showinfo("Poistettu", "Pohja poistettu! / Template deleted!")
                else:
                    messagebox.showerror("Virhe", "Poisto epäonnistui! / Delete failed!")
        
        tk.Button(
            button_frame,
            text="Lataa / Load",
            command=load_selected,
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Poista / Delete",
            command=delete_selected,
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Peruuta / Cancel",
            command=template_window.destroy,
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def exit_app(self):
        """Lopeta sovellus / Exit application"""
        if messagebox.askyesno("Lopeta", "Haluatko varmasti lopettaa? / Do you want to exit?"):
            self.root.quit()


class ReceiptAppTerminal:
    """Terminaalisovellus / Terminal application"""
    
    def __init__(self):
        self.receipt = Receipt()
        self.storage = OfflineStorage()
        self.template_manager = TemplateManager()
        self.running = True
    
    def print_colored(self, text: str, color: str = ""):
        """Tulosta värillisenä jos colorama käytettävissä / Print colored if colorama available"""
        if COLORAMA_AVAILABLE and color:
            colors = {
                "green": Fore.GREEN,
                "red": Fore.RED,
                "yellow": Fore.YELLOW,
                "blue": Fore.BLUE,
                "cyan": Fore.CYAN,
            }
            print(colors.get(color, "") + text + Style.RESET_ALL)
        else:
            print(text)
    
    def show_menu(self):
        """Näytä valikko / Show menu"""
        print("\n" + "=" * 50)
        self.print_colored("KUITTITULOSTIN - HRK RECEIPT PRINTER", "cyan")
        print("=" * 50)
        print("1. Lisää tuote / Add product")
        print("2. Poista tuote / Remove product")
        print("3. Näytä ostoskori / Show cart")
        print("4. Tulosta kuitti / Print receipt")
        print("5. Tallenna PNG / Save PNG")
        print("6. 💾 Tallenna offline / Save offline")
        print("7. ⚙️ Asetukset / Settings")
        print("8. 📋 Historia / History")
        print("9. 📝 Tallenna pohja / Save template")
        print("a. 📂 Lataa pohja / Load template")
        print("c. Tyhjennä / Clear")
        print("0. Lopeta / Exit")
        print("=" * 50)
    
    def add_product_interactive(self):
        """Lisää tuote interaktiivisesti / Add product interactively"""
        try:
            self.print_colored("\n--- Lisää tuote / Add Product ---", "green")
            name = input("Tuotenimi / Product name: ").strip()
            if not name:
                self.print_colored("Tuotenimi ei voi olla tyhjä! / Product name cannot be empty!", "red")
                return
            
            qty_str = input("Määrä / Quantity: ").strip()
            quantity = int(qty_str)
            
            price_str = input("Hinta (€) / Price (€): ").strip()
            price = float(price_str)
            
            if self.receipt.add_product(name, quantity, price):
                self.print_colored("✓ Tuote lisätty! / Product added!", "green")
            else:
                self.print_colored("✗ Virheelliset arvot! / Invalid values!", "red")
                
        except ValueError:
            self.print_colored("✗ Virheellinen syöte! / Invalid input!", "red")
        except KeyboardInterrupt:
            print("\n")
    
    def remove_product_interactive(self):
        """Poista tuote interaktiivisesti / Remove product interactively"""
        if not self.receipt.products:
            self.print_colored("Ostoskori on tyhjä! / Cart is empty!", "yellow")
            return
        
        self.show_cart()
        try:
            index_str = input("\nPoistettavan tuotteen numero / Product number to remove: ").strip()
            index = int(index_str) - 1
            
            if self.receipt.remove_product(index):
                self.print_colored("✓ Tuote poistettu! / Product removed!", "green")
            else:
                self.print_colored("✗ Virheellinen numero! / Invalid number!", "red")
                
        except ValueError:
            self.print_colored("✗ Virheellinen syöte! / Invalid input!", "red")
        except KeyboardInterrupt:
            print("\n")
    
    def show_cart(self):
        """Näytä ostoskori / Show cart"""
        print("\n" + "=" * 50)
        self.print_colored("OSTOSKORI / SHOPPING CART", "blue")
        print("=" * 50)
        
        if not self.receipt.products:
            self.print_colored("Ostoskori on tyhjä! / Cart is empty!", "yellow")
            return
        
        for i, product in enumerate(self.receipt.products, 1):
            print(f"{i}. {product.name}")
            print(f"   {product.quantity} kpl x {product.price:.2f} € = {product.total():.2f} €")
        
        print("-" * 50)
        print(f"Välisumma: {self.receipt.get_subtotal():.2f} €")
        print(f"ALV 24%: {self.receipt.get_vat():.2f} €")
        print("=" * 50)
        self.print_colored(f"YHTEENSÄ: {self.receipt.get_total():.2f} €", "green")
        print("=" * 50)
    
    def print_receipt_interactive(self):
        """Tulosta kuitti / Print receipt"""
        if not self.receipt.products:
            self.print_colored("Lisää tuotteita ensin! / Add products first!", "yellow")
            return
        
        text = self.receipt.generate_text()
        print("\n" + text)
        
        try:
            choice = input("\nTulostetaanko tulostimeen? (k/e) / Print to printer? (y/n): ").strip().lower()
            if choice in ['k', 'y', 'yes', 'kyllä']:
                if ReceiptPrinter.print_to_printer(text):
                    self.print_colored("✓ Kuitti lähetetty tulostimeen! / Receipt sent to printer!", "green")
                else:
                    self.print_colored("✗ Tulostus epäonnistui! / Print failed!", "red")
        except KeyboardInterrupt:
            print("\n")
    
    def save_png_interactive(self):
        """Tallenna PNG / Save PNG"""
        if not self.receipt.products:
            self.print_colored("Lisää tuotteita ensin! / Add products first!", "yellow")
            return
        
        if not PILLOW_AVAILABLE:
            self.print_colored("✗ Pillow-kirjasto puuttuu! Asenna: pip install pillow", "red")
            self.print_colored("✗ Pillow library missing! Install: pip install pillow", "red")
            return
        
        try:
            default_name = f"kuitti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = input(f"Tiedostonimi [{default_name}]: ").strip()
            if not filepath:
                filepath = default_name
            
            text = self.receipt.generate_text()
            if ReceiptPrinter.save_as_png(text, filepath):
                self.print_colored(f"✓ Kuitti tallennettu: {filepath}", "green")
            else:
                self.print_colored("✗ Tallennus epäonnistui! / Save failed!", "red")
        except KeyboardInterrupt:
            print("\n")
    
    def clear_cart(self):
        """Tyhjennä ostoskori / Clear cart"""
        if not self.receipt.products:
            self.print_colored("Ostoskori on jo tyhjä! / Cart is already empty!", "yellow")
            return
        
        try:
            choice = input("Tyhjennetäänkö ostoskori? (k/e) / Clear cart? (y/n): ").strip().lower()
            if choice in ['k', 'y', 'yes', 'kyllä']:
                self.receipt.products.clear()
                self.print_colored("✓ Ostoskori tyhjennetty! / Cart cleared!", "green")
        except KeyboardInterrupt:
            print("\n")
    
    def save_offline_interactive(self):
        """Tallenna offline / Save offline"""
        if not self.receipt.products:
            self.print_colored("Lisää tuotteita ensin! / Add products first!", "yellow")
            return
        
        if self.storage.save_receipt(self.receipt):
            self.print_colored(f"✓ Kuitti tallennettu offline-tilaan! / Receipt saved offline!", "green")
            self.print_colored(f"Kansio / Directory: {self.storage.storage_dir}", "cyan")
        else:
            self.print_colored("✗ Tallennus epäonnistui! / Save failed!", "red")
    
    def show_settings_interactive(self):
        """Asetukset / Settings"""
        while True:
            print("\n" + "=" * 50)
            self.print_colored("ASETUKSET / SETTINGS", "cyan")
            print("=" * 50)
            print("1. Muokkaa yritystietoja / Edit company info")
            print("2. Muokkaa maksutietoja / Edit payment info")
            print("3. Luo ASCII-logo / Create ASCII logo")
            print("4. Lisää huomioita / Add notes")
            print("5. Takaisin / Back")
            print("=" * 50)
            
            try:
                choice = input("\nValitse / Choose: ").strip()
                
                if choice == "1":
                    self._edit_company_info()
                elif choice == "2":
                    self._edit_payment_info()
                elif choice == "3":
                    self._create_ascii_logo()
                elif choice == "4":
                    self._add_notes()
                elif choice == "5":
                    break
            except KeyboardInterrupt:
                print("\n")
                break
    
    def _edit_company_info(self):
        """Muokkaa yritystietoja / Edit company info"""
        print("\n--- Yritystiedot / Company Info ---")
        name = input(f"Nimi [{self.receipt.company_info['name']}]: ").strip() or self.receipt.company_info['name']
        business_id = input(f"Y-tunnus [{self.receipt.company_info['business_id']}]: ").strip() or self.receipt.company_info['business_id']
        address = input(f"Osoite [{self.receipt.company_info['address']}]: ").strip() or self.receipt.company_info['address']
        phone = input(f"Puhelin [{self.receipt.company_info['phone']}]: ").strip() or self.receipt.company_info['phone']
        email = input(f"Email [{self.receipt.company_info.get('email', '')}]: ").strip() or self.receipt.company_info.get('email', '')
        website = input(f"Verkkosivu [{self.receipt.company_info.get('website', '')}]: ").strip() or self.receipt.company_info.get('website', '')
        
        self.receipt.update_company_info(
            name=name,
            business_id=business_id,
            address=address,
            phone=phone,
            email=email,
            website=website
        )
        
        self.print_colored("✓ Yritystiedot päivitetty! / Company info updated!", "green")
    
    def _edit_payment_info(self):
        """Muokkaa maksutietoja / Edit payment info"""
        print("\n--- Maksutiedot / Payment Info ---")
        print("Maksutavat / Payment methods:")
        print("1. Käteinen / Cash")
        print("2. Kortti / Card")
        print("3. Lasku / Invoice")
        print("4. Verkkopankki / Online banking")
        
        method_choice = input("Valitse / Choose: ").strip()
        methods = {
            "1": "Käteinen / Cash",
            "2": "Kortti / Card",
            "3": "Lasku / Invoice",
            "4": "Verkkopankki / Online banking"
        }
        method = methods.get(method_choice, "Käteinen / Cash")
        
        card_type = input("Korttityyppi / Card type (jos korttimaksu / if card): ").strip()
        transaction_id = input("Tapahtumatunnus / Transaction ID: ").strip()
        bank_ref = input("Pankkiviite / Bank reference: ").strip()
        
        self.receipt.set_payment_info(method, card_type, transaction_id, bank_ref)
        self.print_colored("✓ Maksutiedot päivitetty! / Payment info updated!", "green")
    
    def _create_ascii_logo(self):
        """Luo ASCII-logo / Create ASCII logo"""
        print("\n--- ASCII Logo Generator ---")
        text = input("Logo-teksti / Logo text: ").strip()
        
        if not text:
            self.print_colored("Tyhjä teksti! / Empty text!", "yellow")
            return
        
        print("\nTyylit / Styles:")
        print("1. box - Laatikko / Box")
        print("2. stars - Tähdet / Stars")
        print("3. double - Kaksoisviiva / Double line")
        print("4. simple - Yksinkertainen / Simple")
        print("5. banner - Banneri / Banner")
        
        style_choice = input("Valitse tyyli / Choose style [1-5]: ").strip()
        styles = {"1": "box", "2": "stars", "3": "double", "4": "simple", "5": "banner"}
        style = styles.get(style_choice, "box")
        
        self.receipt.set_custom_logo(text, style)
        
        print("\nEsikatselu / Preview:")
        print(self.receipt.custom_logo)
        self.print_colored("✓ Logo luotu! / Logo created!", "green")
    
    def _add_notes(self):
        """Lisää huomioita / Add notes"""
        print("\n--- Huomiot / Notes ---")
        print("Kirjoita huomiot (tyhjä rivi lopettaa / empty line to finish):")
        
        lines = []
        while True:
            try:
                line = input()
                if not line:
                    break
                lines.append(line)
            except KeyboardInterrupt:
                break
        
        self.receipt.receipt_notes = "\n".join(lines)
        self.print_colored("✓ Huomiot lisätty! / Notes added!", "green")
    
    def show_history_interactive(self):
        """Näytä historia / Show history"""
        history = self.storage.load_history()
        
        if not history:
            self.print_colored("Historia on tyhjä! / History is empty!", "yellow")
            return
        
        print("\n" + "=" * 50)
        self.print_colored("KUITTIHISTORIA / RECEIPT HISTORY", "cyan")
        print("=" * 50)
        
        for i, entry in enumerate(reversed(history), 1):
            print(f"\n{i}. {entry.get('timestamp', '')}")
            print(f"   Yritys / Company: {entry.get('company', '')}")
            print(f"   Summa / Total: {entry.get('total', 0):.2f} €")
            print(f"   Maksutapa / Payment: {entry.get('payment_method', '')}")
            print(f"   Tiedosto / File: {entry.get('filename', '')}")
        
        print("=" * 50)
        
        try:
            choice = input("\nLataa kuitti numerolla (tyhjä = peruuta) / Load receipt by number (empty = cancel): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(history):
                    entry = list(reversed(history))[idx]
                    filename = entry.get("filename", "")
                    
                    loaded_receipt = self.storage.load_receipt(filename)
                    if loaded_receipt:
                        self.receipt = loaded_receipt
                        self.print_colored("✓ Kuitti ladattu! / Receipt loaded!", "green")
                    else:
                        self.print_colored("✗ Lataus epäonnistui! / Load failed!", "red")
                else:
                    self.print_colored("✗ Virheellinen numero! / Invalid number!", "red")
        except KeyboardInterrupt:
            print("\n")
    
    def save_template_interactive(self):
        """Tallenna kuittipohja / Save receipt template"""
        print("\n" + "=" * 50)
        self.print_colored("TALLENNA KUITTIPOHJA / SAVE RECEIPT TEMPLATE", "cyan")
        print("=" * 50)
        
        try:
            template_name = input("Anna pohjan nimi / Enter template name: ").strip()
            
            if not template_name:
                self.print_colored("Pohjan nimi ei voi olla tyhjä! / Template name cannot be empty!", "red")
                return
            
            if self.template_manager.save_template(self.receipt, template_name):
                self.print_colored(f"✓ Pohja '{template_name}' tallennettu!", "green")
                self.print_colored(f"✓ Template '{template_name}' saved!", "green")
                print("\nTallennetut tiedot / Saved information:")
                print(f"  • Yritystiedot / Company info: {self.receipt.company_info['name']}")
                print(f"  • Maksutapa / Payment: {self.receipt.payment_info['method']}")
                print(f"  • Logo-tyyli / Logo style: {self.receipt.logo_style}")
            else:
                self.print_colored("✗ Pohjan tallennus epäonnistui! / Template save failed!", "red")
        
        except KeyboardInterrupt:
            print("\n")
    
    def load_template_interactive(self):
        """Lataa kuittipohja / Load receipt template"""
        templates = self.template_manager.list_templates()
        
        if not templates:
            self.print_colored("Ei tallennettuja pohjia! / No saved templates!", "yellow")
            print("Tallenna ensin pohja valinnalla 9.")
            return
        
        print("\n" + "=" * 50)
        self.print_colored("LADAA KUITTIPOHJA / LOAD RECEIPT TEMPLATE", "cyan")
        print("=" * 50)
        
        print("\nTallennetut pohjat / Saved templates:")
        for i, template in enumerate(templates, 1):
            template_info = self.template_manager.get_template_info(template)
            if template_info:
                company = template_info.get("company_info", {}).get("name", "N/A")
                created = template_info.get("created", "")
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created)
                        created_str = created_dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        created_str = created
                else:
                    created_str = ""
                
                print(f"{i}. {template}")
                print(f"   Yritys / Company: {company}")
                if created_str:
                    print(f"   Luotu / Created: {created_str}")
            else:
                print(f"{i}. {template}")
        
        print("=" * 50)
        
        try:
            choice = input("\nValitse pohjan numero (tyhjä = peruuta) / Choose template number (empty = cancel): ").strip()
            
            if not choice:
                return
            
            if not choice.isdigit():
                self.print_colored("✗ Virheellinen valinta! / Invalid choice!", "red")
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                template_name = templates[idx]
                
                # Kysytään säilytetäänkö tuotteet
                if self.receipt.products:
                    keep = input("\nSäilytetäänkö nykyiset tuotteet? (k/e) / Keep current products? (y/n): ").strip().lower()
                    keep_products = keep in ['k', 'y', 'yes', 'kyllä']
                    
                    if keep_products:
                        old_products = self.receipt.products.copy()
                else:
                    keep_products = False
                    old_products = []
                
                # Lataa pohja
                loaded_receipt = self.template_manager.load_template(template_name)
                
                if loaded_receipt:
                    # Palauta tuotteet tarvittaessa
                    if keep_products:
                        for product in old_products:
                            loaded_receipt.add_product(product.name, product.quantity, product.price)
                    
                    self.receipt = loaded_receipt
                    self.print_colored(f"✓ Pohja '{template_name}' ladattu!", "green")
                    self.print_colored(f"✓ Template '{template_name}' loaded!", "green")
                    print("\nLadatut tiedot / Loaded information:")
                    print(f"  • Yritys / Company: {self.receipt.company_info['name']}")
                    print(f"  • Maksutapa / Payment: {self.receipt.payment_info['method']}")
                    print(f"  • Logo-tyyli / Logo style: {self.receipt.logo_style}")
                else:
                    self.print_colored("✗ Pohjan lataus epäonnistui! / Template load failed!", "red")
            else:
                self.print_colored("✗ Virheellinen numero! / Invalid number!", "red")
        
        except KeyboardInterrupt:
            print("\n")
    
    def run(self):
        """Pääsilmukka / Main loop"""
        self.print_colored("\n=== Kuittitulostin käynnistetty terminaalitilassa ===", "cyan")
        self.print_colored("=== Receipt Printer started in terminal mode ===", "cyan")
        
        while self.running:
            try:
                self.show_menu()
                choice = input("\nValitse toiminto / Choose action: ").strip()
                
                if choice == "1":
                    self.add_product_interactive()
                elif choice == "2":
                    self.remove_product_interactive()
                elif choice == "3":
                    self.show_cart()
                elif choice == "4":
                    self.print_receipt_interactive()
                elif choice == "5":
                    self.save_png_interactive()
                elif choice == "6":
                    self.save_offline_interactive()
                elif choice == "7":
                    self.show_settings_interactive()
                elif choice == "8":
                    self.show_history_interactive()
                elif choice == "9":
                    self.save_template_interactive()
                elif choice.lower() == "a":
                    self.load_template_interactive()
                elif choice.lower() == "c":
                    self.clear_cart()
                elif choice == "0":
                    self.print_colored("\nKiitos käytöstä! / Thank you!", "green")
                    self.running = False
                else:
                    self.print_colored("Virheellinen valinta! / Invalid choice!", "red")
                    
            except KeyboardInterrupt:
                print("\n")
                self.print_colored("Ohjelma keskeytetty. / Program interrupted.", "yellow")
                self.running = False
            except Exception as e:
                self.print_colored(f"Virhe: {e} / Error: {e}", "red")


def main():
    """Pääohjelma / Main program"""
    print("Käynnistetään kuittitulostin... / Starting receipt printer...")
    
    # Tarkista Python-versio / Check Python version
    if sys.version_info < (3, 8):
        print("VAROITUS: Python 3.8 tai uudempi suositellaan!")
        print("WARNING: Python 3.8 or newer is recommended!")
    
    # Valitse GUI tai terminaali / Choose GUI or terminal
    if GUI_AVAILABLE and "--terminal" not in sys.argv:
        # Käynnistä GUI / Start GUI
        root = tk.Tk()
        app = ReceiptAppGUI(root)
        root.mainloop()
    else:
        # Käynnistä terminaalisovellus / Start terminal application
        if not GUI_AVAILABLE:
            print("Tkinter ei ole käytettävissä. Käytetään terminaalitilaa.")
            print("Tkinter not available. Using terminal mode.")
        app = ReceiptAppTerminal()
        app.run()


if __name__ == "__main__":
    main()
