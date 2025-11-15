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
    from tkinter import ttk, messagebox, filedialog
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
            "phone": "+358 40 123 4567"
        }
    
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
    
    def generate_text(self) -> str:
        """Luo tekstimuotoinen kuitti / Generate text receipt"""
        lines = []
        lines.append(self.LOGO)
        lines.append(f"\n{self.company_info['name']}")
        lines.append(f"Y-tunnus: {self.company_info['business_id']}")
        lines.append(f"{self.company_info['address']}")
        lines.append(f"Puh: {self.company_info['phone']}")
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
        lines.append("\nKiitos ostoksesta! / Thank you for your purchase!")
        lines.append("\n")
        
        return "\n".join(lines)


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
        self.root.geometry("700x600")
        
        self.receipt = Receipt()
        
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
    
    def exit_app(self):
        """Lopeta sovellus / Exit application"""
        if messagebox.askyesno("Lopeta", "Haluatko varmasti lopettaa? / Do you want to exit?"):
            self.root.quit()


class ReceiptAppTerminal:
    """Terminaalisovellus / Terminal application"""
    
    def __init__(self):
        self.receipt = Receipt()
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
        print("6. Tyhjennä / Clear")
        print("7. Lopeta / Exit")
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
                    self.clear_cart()
                elif choice == "7":
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
