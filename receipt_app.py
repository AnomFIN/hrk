#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kuittisovellus - Receipt Application
Täydellinen kuittisovellus GUI:lla ja terminaali-tuella
"""

import sys
import platform
import subprocess
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# Yritä tuoda GUI-kirjastot
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("VAROITUS: Tkinter ei ole käytettävissä. Käytetään terminaaliversiota.")

# Yritä tuoda PIL (Pillow) PNG-tallennukseen
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("VAROITUS: Pillow ei ole asennettu. PNG-tallennus ei ole käytettävissä.")
    print("Asenna komennolla: pip install pillow")

# Colorama terminaalin väreihin (valinnainen)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# ========== VAKIOT ==========
ALV_KANTA = Decimal('0.24')  # 24% ALV
YRITYS_NIMI = "LV Electronics"
YRITYS_OSOITE = "Hämeentie 123, 00500 Helsinki"
YRITYS_PUHELIN = "Tel: +358 50 123 4567"
YRITYS_Y_TUNNUS = "Y-tunnus: 1234567-8"

# ASCII Logo (LV-tyylinen)
ASCII_LOGO = """
╔═══════════════════════════╗
║                           ║
║    ██╗     ██╗   ██╗     ║
║    ██║     ██║   ██║     ║
║    ██║     ██║   ██║     ║
║    ██║     ╚██╗ ██╔╝     ║
║    ███████╗ ╚████╔╝      ║
║    ╚══════╝  ╚═══╝       ║
║                           ║
║   LV Electronics          ║
║                           ║
╚═══════════════════════════╝
"""


# ========== TUOTELUOKKA ==========
class Tuote:
    """Yksittäinen tuote kuitilla"""
    
    def __init__(self, nimi, maara, hinta):
        self.nimi = nimi
        self.maara = int(maara)
        self.hinta = Decimal(str(hinta))
    
    def yhteensa(self):
        """Tuotteen kokonaishinta"""
        return self.hinta * self.maara
    
    def __str__(self):
        return f"{self.nimi} x{self.maara} @ {self.hinta:.2f}€ = {self.yhteensa():.2f}€"


# ========== KUITTI-LOGIIKKA ==========
class Kuitti:
    """Kuitin hallinta ja laskenta"""
    
    def __init__(self):
        self.tuotteet = []
    
    def lisaa_tuote(self, nimi, maara, hinta):
        """Lisää tuote kuittiin"""
        try:
            tuote = Tuote(nimi, maara, hinta)
            self.tuotteet.append(tuote)
            return True
        except (ValueError, TypeError) as e:
            print(f"Virhe tuotteen lisäämisessä: {e}")
            return False
    
    def poista_tuote(self, indeksi):
        """Poista tuote indeksin perusteella"""
        try:
            if 0 <= indeksi < len(self.tuotteet):
                self.tuotteet.pop(indeksi)
                return True
            return False
        except Exception as e:
            print(f"Virhe tuotteen poistamisessa: {e}")
            return False
    
    def tyhjenna(self):
        """Tyhjennä kaikki tuotteet"""
        self.tuotteet.clear()
    
    def valisumma(self):
        """Laske välisumma (ilman ALV:ia)"""
        return sum(tuote.yhteensa() for tuote in self.tuotteet)
    
    def alv_summa(self):
        """Laske ALV-summa"""
        return self.valisumma() * ALV_KANTA
    
    def kokonaissumma(self):
        """Laske kokonaissumma (sisältää ALV:in)"""
        return self.valisumma() + self.alv_summa()
    
    def muodosta_kuittiteksti(self):
        """Muodosta kuitin tekstimuoto"""
        rivit = []
        rivit.append(ASCII_LOGO)
        rivit.append("")
        rivit.append(f"{YRITYS_NIMI}")
        rivit.append(f"{YRITYS_OSOITE}")
        rivit.append(f"{YRITYS_PUHELIN}")
        rivit.append(f"{YRITYS_Y_TUNNUS}")
        rivit.append("")
        rivit.append("=" * 50)
        rivit.append(f"KUITTI - {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        rivit.append("=" * 50)
        rivit.append("")
        
        if not self.tuotteet:
            rivit.append("(Ei tuotteita)")
        else:
            rivit.append(f"{'Tuote':<25} {'Määrä':>5} {'À hinta':>10} {'Yht.':>10}")
            rivit.append("-" * 50)
            for tuote in self.tuotteet:
                rivit.append(
                    f"{tuote.nimi[:25]:<25} "
                    f"{tuote.maara:>5} "
                    f"{tuote.hinta:>10.2f}€ "
                    f"{tuote.yhteensa():>10.2f}€"
                )
        
        rivit.append("")
        rivit.append("-" * 50)
        rivit.append(f"{'Välisumma (veroton):':<30} {self.valisumma():>18.2f}€")
        rivit.append(f"{'ALV 24%:':<30} {self.alv_summa():>18.2f}€")
        rivit.append("=" * 50)
        rivit.append(f"{'YHTEENSÄ:':<30} {self.kokonaissumma():>18.2f}€")
        rivit.append("=" * 50)
        rivit.append("")
        rivit.append("Kiitos käynnistänne!")
        rivit.append("")
        
        return "\n".join(rivit)


# ========== TULOSTUS ==========
def tulosta_kuitti(kuittiteksti):
    """Tulosta kuitti oletustulostimeen"""
    try:
        os_name = platform.system()
        
        if os_name == "Windows":
            # Windows: Käytä notepad /p
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(kuittiteksti)
                temp_path = f.name
            
            subprocess.run(['notepad', '/p', temp_path], check=True)
            print("Kuitti lähetetty tulostimeen (Windows).")
            return True
            
        elif os_name == "Linux":
            # Linux: Käytä lp tai lpr
            try:
                process = subprocess.Popen(['lp'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=kuittiteksti)
                print("Kuitti lähetetty tulostimeen (Linux - lp).")
                return True
            except FileNotFoundError:
                try:
                    process = subprocess.Popen(['lpr'], stdin=subprocess.PIPE, text=True)
                    process.communicate(input=kuittiteksti)
                    print("Kuitti lähetetty tulostimeen (Linux - lpr).")
                    return True
                except FileNotFoundError:
                    print("VIRHE: Tulostuskomentoa (lp tai lpr) ei löytynyt.")
                    return False
        
        elif os_name == "Darwin":
            # macOS: Käytä lpr
            process = subprocess.Popen(['lpr'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=kuittiteksti)
            print("Kuitti lähetetty tulostimeen (macOS).")
            return True
        
        else:
            print(f"VIRHE: Tulostus ei tuettu käyttöjärjestelmässä: {os_name}")
            return False
            
    except Exception as e:
        print(f"VIRHE tulostuksessa: {e}")
        return False


# ========== PNG-TALLENNUS ==========
def tallenna_png(kuittiteksti, tiedostonimi="kuitti.png"):
    """Tallenna kuitti PNG-kuvaksi"""
    if not PIL_AVAILABLE:
        print("VIRHE: Pillow-kirjasto ei ole asennettu. PNG-tallennus ei ole mahdollista.")
        return False
    
    try:
        # Laske tarvittava korkeus
        rivit = kuittiteksti.split('\n')
        leveys = 600
        fonttikoko = 12
        rivikorkeus = fonttikoko + 4
        korkeus = len(rivit) * rivikorkeus + 40
        
        # Luo kuva
        img = Image.new('RGB', (leveys, korkeus), color='white')
        draw = ImageDraw.Draw(img)
        
        # Yritä ladata monospace-fontti, muuten käytä oletusta
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", fonttikoko)
        except:
            try:
                font = ImageFont.truetype("cour.ttf", fonttikoko)  # Windows Courier
            except:
                font = ImageFont.load_default()
        
        # Piirrä teksti
        y = 20
        for rivi in rivit:
            draw.text((10, y), rivi, fill='black', font=font)
            y += rivikorkeus
        
        # Tallenna
        img.save(tiedostonimi)
        print(f"Kuitti tallennettu: {tiedostonimi}")
        return True
        
    except Exception as e:
        print(f"VIRHE PNG-tallennuksessa: {e}")
        return False


# ========== GUI-SOVELLUS ==========
class KuittiGUI:
    """Tkinter GUI-sovellus"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Kuittisovellus - LV Electronics")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        self.kuitti = Kuitti()
        
        self.luo_gui()
    
    def luo_gui(self):
        """Luo GUI-komponentit"""
        
        # Yläreunan otsikko
        otsikko = tk.Label(
            self.root, 
            text="🧾 LV Electronics - Kuittisovellus", 
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=10
        )
        otsikko.pack(fill=tk.X)
        
        # Pääkehys
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === VASEN PUOLI: Tuotteiden lisäys ===
        vasen_frame = tk.LabelFrame(main_frame, text="Lisää tuote", padx=10, pady=10)
        vasen_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        tk.Label(vasen_frame, text="Tuotteen nimi:").grid(row=0, column=0, sticky="w", pady=2)
        self.nimi_entry = tk.Entry(vasen_frame, width=30)
        self.nimi_entry.grid(row=0, column=1, pady=2)
        
        tk.Label(vasen_frame, text="Määrä (kpl):").grid(row=1, column=0, sticky="w", pady=2)
        self.maara_entry = tk.Entry(vasen_frame, width=30)
        self.maara_entry.grid(row=1, column=1, pady=2)
        self.maara_entry.insert(0, "1")
        
        tk.Label(vasen_frame, text="Hinta (€/kpl):").grid(row=2, column=0, sticky="w", pady=2)
        self.hinta_entry = tk.Entry(vasen_frame, width=30)
        self.hinta_entry.grid(row=2, column=1, pady=2)
        
        tk.Button(
            vasen_frame, 
            text="✚ Lisää tuote", 
            command=self.lisaa_tuote_gui,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            pady=5
        ).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        
        # === OIKEA PUOLI: Tuotelista ===
        oikea_frame = tk.LabelFrame(main_frame, text="Tuotteet kuitilla", padx=10, pady=10)
        oikea_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Treeview tuotelistalle
        columns = ("Tuote", "Määrä", "Hinta", "Yhteensä")
        self.tree = ttk.Treeview(oikea_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("Tuote", text="Tuote")
        self.tree.heading("Määrä", text="Määrä")
        self.tree.heading("Hinta", text="Hinta (€)")
        self.tree.heading("Yhteensä", text="Yhteensä (€)")
        
        self.tree.column("Tuote", width=180)
        self.tree.column("Määrä", width=60, anchor="center")
        self.tree.column("Hinta", width=80, anchor="e")
        self.tree.column("Yhteensä", width=100, anchor="e")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(oikea_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Button(
            oikea_frame, 
            text="🗑 Poista valittu tuote", 
            command=self.poista_tuote_gui,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9)
        ).pack(pady=5, fill=tk.X)
        
        # === SUMMAT ===
        summa_frame = tk.LabelFrame(main_frame, text="Yhteenveto", padx=10, pady=10, bg="#ecf0f1")
        summa_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        
        self.valisumma_label = tk.Label(summa_frame, text="Välisumma: 0.00€", font=("Arial", 11), bg="#ecf0f1")
        self.valisumma_label.pack(anchor="w")
        
        self.alv_label = tk.Label(summa_frame, text="ALV (24%): 0.00€", font=("Arial", 11), bg="#ecf0f1")
        self.alv_label.pack(anchor="w")
        
        self.yhteensa_label = tk.Label(
            summa_frame, 
            text="YHTEENSÄ: 0.00€", 
            font=("Arial", 14, "bold"), 
            fg="#27ae60",
            bg="#ecf0f1"
        )
        self.yhteensa_label.pack(anchor="w", pady=5)
        
        # === TOIMINTOPAINIKKEET ===
        toiminto_frame = tk.Frame(main_frame)
        toiminto_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(
            toiminto_frame, 
            text="🖨 Tulosta kuitti", 
            command=self.tulosta_gui,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toiminto_frame, 
            text="💾 Tallenna PNG", 
            command=self.tallenna_png_gui,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toiminto_frame, 
            text="🔄 Tyhjennä", 
            command=self.tyhjenna_gui,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toiminto_frame, 
            text="❌ Lopeta", 
            command=self.lopeta_gui,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Grid-konfiguraatio
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
    
    def lisaa_tuote_gui(self):
        """Lisää tuote GUI:sta"""
        nimi = self.nimi_entry.get().strip()
        maara = self.maara_entry.get().strip()
        hinta = self.hinta_entry.get().strip()
        
        if not nimi or not maara or not hinta:
            messagebox.showwarning("Puuttuvia tietoja", "Täytä kaikki kentät!")
            return
        
        try:
            if self.kuitti.lisaa_tuote(nimi, maara, hinta):
                self.paivita_lista()
                self.paivita_summat()
                # Tyhjennä kentät
                self.nimi_entry.delete(0, tk.END)
                self.maara_entry.delete(0, tk.END)
                self.maara_entry.insert(0, "1")
                self.hinta_entry.delete(0, tk.END)
                self.nimi_entry.focus()
            else:
                messagebox.showerror("Virhe", "Tuotteen lisääminen epäonnistui!")
        except Exception as e:
            messagebox.showerror("Virhe", f"Virhe tuotteen lisäämisessä:\n{e}")
    
    def poista_tuote_gui(self):
        """Poista valittu tuote GUI:sta"""
        valittu = self.tree.selection()
        if not valittu:
            messagebox.showwarning("Ei valintaa", "Valitse ensin poistettava tuote!")
            return
        
        indeksi = self.tree.index(valittu[0])
        if self.kuitti.poista_tuote(indeksi):
            self.paivita_lista()
            self.paivita_summat()
    
    def tyhjenna_gui(self):
        """Tyhjennä kaikki tuotteet"""
        if messagebox.askyesno("Tyhjennä", "Haluatko varmasti tyhjentää kaikki tuotteet?"):
            self.kuitti.tyhjenna()
            self.paivita_lista()
            self.paivita_summat()
    
    def paivita_lista(self):
        """Päivitä tuotelista"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for tuote in self.kuitti.tuotteet:
            self.tree.insert("", tk.END, values=(
                tuote.nimi,
                tuote.maara,
                f"{tuote.hinta:.2f}",
                f"{tuote.yhteensa():.2f}"
            ))
    
    def paivita_summat(self):
        """Päivitä summatiedot"""
        self.valisumma_label.config(text=f"Välisumma: {self.kuitti.valisumma():.2f}€")
        self.alv_label.config(text=f"ALV (24%): {self.kuitti.alv_summa():.2f}€")
        self.yhteensa_label.config(text=f"YHTEENSÄ: {self.kuitti.kokonaissumma():.2f}€")
    
    def tulosta_gui(self):
        """Tulosta kuitti"""
        if not self.kuitti.tuotteet:
            messagebox.showwarning("Tyhjä kuitti", "Lisää ensin tuotteita kuittiin!")
            return
        
        kuittiteksti = self.kuitti.muodosta_kuittiteksti()
        if tulosta_kuitti(kuittiteksti):
            messagebox.showinfo("Onnistui", "Kuitti lähetetty tulostimeen!")
        else:
            messagebox.showerror("Virhe", "Tulostus epäonnistui. Katso konsolista lisätietoja.")
    
    def tallenna_png_gui(self):
        """Tallenna kuitti PNG:ksi"""
        if not self.kuitti.tuotteet:
            messagebox.showwarning("Tyhjä kuitti", "Lisää ensin tuotteita kuittiin!")
            return
        
        if not PIL_AVAILABLE:
            messagebox.showerror("Virhe", "Pillow-kirjasto ei ole asennettu.\nAsenna: pip install pillow")
            return
        
        tiedosto = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG-kuva", "*.png"), ("Kaikki tiedostot", "*.*")],
            initialfile=f"kuitti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        
        if tiedosto:
            kuittiteksti = self.kuitti.muodosta_kuittiteksti()
            if tallenna_png(kuittiteksti, tiedosto):
                messagebox.showinfo("Onnistui", f"Kuitti tallennettu:\n{tiedosto}")
            else:
                messagebox.showerror("Virhe", "PNG-tallennus epäonnistui!")
    
    def lopeta_gui(self):
        """Lopeta sovellus"""
        if messagebox.askyesno("Lopeta", "Haluatko varmasti lopettaa?"):
            self.root.quit()
            self.root.destroy()


# ========== TERMINAALI-VERSIO ==========
def terminaali_versio():
    """Yksinkertainen terminaaliversio"""
    kuitti = Kuitti()
    
    def tulosta_valikko():
        if COLORAMA_AVAILABLE:
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}KUITTISOVELLUS - LV Electronics")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        else:
            print("\n" + "="*50)
            print("KUITTISOVELLUS - LV Electronics")
            print("="*50)
        
        print("\n1. Lisää tuote")
        print("2. Poista tuote")
        print("3. Näytä kuitti")
        print("4. Tulosta kuitti")
        print("5. Tallenna kuitti PNG:ksi")
        print("6. Tyhjennä kuitti")
        print("0. Lopeta")
        print()
    
    def nayta_tuotteet():
        if not kuitti.tuotteet:
            print("\n(Ei tuotteita kuitilla)")
        else:
            print(f"\n{'Nro':<5} {'Tuote':<25} {'Määrä':>8} {'Hinta':>10} {'Yht.':>10}")
            print("-" * 70)
            for i, tuote in enumerate(kuitti.tuotteet):
                print(f"{i+1:<5} {tuote.nimi[:25]:<25} {tuote.maara:>8} {tuote.hinta:>10.2f}€ {tuote.yhteensa():>10.2f}€")
            print("-" * 70)
            print(f"{'Välisumma:':<50} {kuitti.valisumma():>18.2f}€")
            print(f"{'ALV 24%:':<50} {kuitti.alv_summa():>18.2f}€")
            print(f"{'YHTEENSÄ:':<50} {kuitti.kokonaissumma():>18.2f}€")
    
    print(ASCII_LOGO)
    print("Tervetuloa! GUI ei ole käytettävissä, käytetään terminaaliversiota.\n")
    
    while True:
        try:
            tulosta_valikko()
            valinta = input("Valitse toiminto: ").strip()
            
            if valinta == "1":
                # Lisää tuote
                print("\n--- Lisää tuote ---")
                nimi = input("Tuotteen nimi: ").strip()
                if not nimi:
                    print("Nimi ei voi olla tyhjä!")
                    continue
                
                try:
                    maara = int(input("Määrä (kpl): ").strip())
                    hinta = float(input("Hinta (€/kpl): ").strip())
                    
                    if kuitti.lisaa_tuote(nimi, maara, hinta):
                        print(f"✓ Tuote '{nimi}' lisätty!")
                    else:
                        print("✗ Tuotteen lisääminen epäonnistui!")
                except ValueError:
                    print("✗ Virheellinen syöte! Määrä ja hinta pitää olla numeroita.")
            
            elif valinta == "2":
                # Poista tuote
                nayta_tuotteet()
                if kuitti.tuotteet:
                    try:
                        nro = int(input("\nPoistettavan tuotteen numero: ").strip())
                        if kuitti.poista_tuote(nro - 1):
                            print("✓ Tuote poistettu!")
                        else:
                            print("✗ Virheellinen numero!")
                    except ValueError:
                        print("✗ Anna numero!")
            
            elif valinta == "3":
                # Näytä kuitti
                nayta_tuotteet()
                if kuitti.tuotteet:
                    print("\n--- Kuitti ---")
                    print(kuitti.muodosta_kuittiteksti())
            
            elif valinta == "4":
                # Tulosta kuitti
                if not kuitti.tuotteet:
                    print("✗ Kuitissa ei ole tuotteita!")
                else:
                    kuittiteksti = kuitti.muodosta_kuittiteksti()
                    if tulosta_kuitti(kuittiteksti):
                        print("✓ Kuitti lähetetty tulostimeen!")
                    else:
                        print("✗ Tulostus epäonnistui!")
            
            elif valinta == "5":
                # Tallenna PNG
                if not kuitti.tuotteet:
                    print("✗ Kuitissa ei ole tuotteita!")
                elif not PIL_AVAILABLE:
                    print("✗ Pillow-kirjasto ei ole asennettu!")
                    print("  Asenna: pip install pillow")
                else:
                    tiedostonimi = input("Anna tiedostonimi (tyhjä = kuitti.png): ").strip()
                    if not tiedostonimi:
                        tiedostonimi = f"kuitti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    
                    kuittiteksti = kuitti.muodosta_kuittiteksti()
                    if tallenna_png(kuittiteksti, tiedostonimi):
                        print(f"✓ Kuitti tallennettu: {tiedostonimi}")
                    else:
                        print("✗ PNG-tallennus epäonnistui!")
            
            elif valinta == "6":
                # Tyhjennä
                vahvistus = input("Haluatko varmasti tyhjentää kuitin? (k/e): ").strip().lower()
                if vahvistus == 'k':
                    kuitti.tyhjenna()
                    print("✓ Kuitti tyhjennetty!")
            
            elif valinta == "0":
                # Lopeta
                print("\nKiitos käytöstä! Näkemiin! 👋")
                break
            
            else:
                print("✗ Tuntematon valinta!")
        
        except KeyboardInterrupt:
            print("\n\nOhjelma keskeytetty. Näkemiin!")
            break
        except Exception as e:
            print(f"\n✗ VIRHE: {e}")
            print("Ohjelma jatkaa...")


# ========== PÄÄOHJELMA ==========
def main():
    """Pääohjelma: käynnistä GUI tai terminaali"""
    
    print("="*60)
    print("   KUITTISOVELLUS - LV Electronics")
    print("="*60)
    print(f"Python-versio: {sys.version}")
    print(f"Käyttöjärjestelmä: {platform.system()} {platform.release()}")
    print(f"GUI (Tkinter): {'Saatavilla' if GUI_AVAILABLE else 'EI saatavilla'}")
    print(f"PNG-tallennus (Pillow): {'Saatavilla' if PIL_AVAILABLE else 'EI saatavilla'}")
    print(f"Värillinen terminaali (colorama): {'Saatavilla' if COLORAMA_AVAILABLE else 'EI saatavilla'}")
    print("="*60)
    
    if GUI_AVAILABLE:
        # Käynnistä GUI
        print("\n🚀 Käynnistetään GUI-sovellus...\n")
        root = tk.Tk()
        app = KuittiGUI(root)
        root.mainloop()
    else:
        # Käytä terminaaliversiota
        print("\n⚠️  GUI ei ole käytettävissä.")
        print("📝 Käytetään terminaaliversiota.\n")
        terminaali_versio()


if __name__ == "__main__":
    main()
