#!/usr/bin/env python3
"""
Täydellinen esimerkki kaikista kuittikone-ominaisuuksista
Complete example of all kuittikone features
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from receipt_app import Receipt, ASCIILogoGenerator, OfflineStorage

def create_complete_receipt():
    """Luo täydellinen kuitti kaikilla ominaisuuksilla"""
    
    print("\n" + "=" * 70)
    print("TÄYDELLINEN KUITTIESIMERKKI / COMPLETE RECEIPT EXAMPLE")
    print("=" * 70)
    
    # 1. Luo kuitti / Create receipt
    print("\n[1/7] Luodaan kuitti / Creating receipt...")
    receipt = Receipt()
    
    # 2. Aseta mukautettu ASCII-logo / Set custom ASCII logo
    print("[2/7] Asetetaan ASCII-logo / Setting ASCII logo...")
    receipt.set_custom_logo("HARJUN RASKASKONE", "banner")
    print("     Logo tyyli / Logo style: banner")
    
    # 3. Päivitä yritystiedot / Update company info
    print("[3/7] Päivitetään yritystiedot / Updating company info...")
    receipt.update_company_info(
        name="Harjun Raskaskone Oy",
        business_id="FI12345678",
        address="Teollisuustie 1, 00100 Helsinki, Suomi",
        phone="+358 40 123 4567",
        email="info@hrk.fi",
        website="www.harjunraskaskone.fi"
    )
    print("     ✓ Yritystiedot päivitetty")
    
    # 4. Lisää tuotteita / Add products
    print("[4/7] Lisätään tuotteita / Adding products...")
    products = [
        ("Kaivinkone 15t - Vuokraus (1 viikko)", 1, 850.00),
        ("Kuorma-auto Mercedes - Vuokraus (3 päivää)", 1, 450.00),
        ("Ajoneuvon kuljetus", 1, 120.00),
        ("Lisävakuutus", 2, 35.00)
    ]
    
    for name, qty, price in products:
        receipt.add_product(name, qty, price)
        print(f"     + {name}: {qty} x {price:.2f} €")
    
    # 5. Aseta maksutiedot / Set payment information
    print("[5/7] Asetetaan maksutiedot / Setting payment info...")
    receipt.set_payment_info(
        method="Kortti / Card",
        card_type="Visa Debit",
        transaction_id=f"TX-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        bank_reference="RF" + datetime.now().strftime('%Y%m%d%H%M')
    )
    print("     ✓ Maksutiedot asetettu")
    print(f"     Tapahtumatunnus / Transaction ID: {receipt.payment_info['transaction_id']}")
    
    # 6. Lisää huomioita / Add notes
    print("[6/7] Lisätään huomioita / Adding notes...")
    receipt.receipt_notes = """
TOIMITUSEHDOT / DELIVERY TERMS:
- Kaivinkone toimitetaan huomenna klo 08:00
- Polttoaine täytetty
- Huoltokirja mukana
- Palautus viimeistään 29.11.2024 klo 16:00

LISÄTIEDOT / ADDITIONAL INFO:
- Asiakas: Rakennus Oy ABC
- Projekti: Uudisrakennus, Espoo
- Yhteyshenkilö: Matti Meikäläinen, +358 50 123 4567
"""
    print("     ✓ Huomiot lisätty")
    
    # 7. Tallenna offline / Save offline
    print("[7/7] Tallennetaan offline-tilaan / Saving offline...")
    storage = OfflineStorage()
    
    if storage.save_receipt(receipt):
        print("     ✓ Kuitti tallennettu offline-tilaan!")
        print(f"     Kansio / Directory: {storage.storage_dir.absolute()}")
        
        # Näytä historia
        history = storage.load_history()
        print(f"\n     Kuitteja historiassa / Receipts in history: {len(history)}")
        
        if history:
            latest = history[-1]
            print(f"     Viimeisin / Latest:")
            print(f"       - Aika / Time: {latest['timestamp']}")
            print(f"       - Summa / Total: {latest['total']:.2f} €")
            print(f"       - Tiedosto / File: {latest['filename']}")
    
    return receipt

def display_receipt(receipt):
    """Näytä kuitti / Display receipt"""
    print("\n" + "=" * 70)
    print("VALMIS KUITTI / COMPLETED RECEIPT")
    print("=" * 70)
    print(receipt.generate_text())
    print("=" * 70)

def show_statistics(receipt):
    """Näytä tilastot / Show statistics"""
    print("\n" + "=" * 70)
    print("TILASTOT / STATISTICS")
    print("=" * 70)
    
    print(f"\nTuotteita yhteensä / Total products: {len(receipt.products)}")
    print(f"Tuoterivejä / Product lines: {sum(p.quantity for p in receipt.products)}")
    print(f"\nVälisumma / Subtotal: {receipt.get_subtotal():.2f} €")
    print(f"ALV 24% / VAT 24%: {receipt.get_vat():.2f} €")
    print(f"YHTEENSÄ / TOTAL: {receipt.get_total():.2f} €")
    
    print(f"\nMaksutapa / Payment method: {receipt.payment_info['method']}")
    print(f"Korttitype / Card type: {receipt.payment_info['card_type']}")
    
    print(f"\nYritys / Company: {receipt.company_info['name']}")
    print(f"Mukautettu logo käytössä / Custom logo: {'Kyllä / Yes' if receipt.custom_logo else 'Ei / No'}")
    print(f"Huomioita / Notes: {'Kyllä / Yes' if receipt.receipt_notes else 'Ei / No'}")

def show_ascii_logos():
    """Näytä eri ASCII-logo-tyylit / Show different ASCII logo styles"""
    print("\n" + "=" * 70)
    print("ASCII LOGO -TYYLIT / ASCII LOGO STYLES")
    print("=" * 70)
    
    text = "HRK"
    styles = ["box", "stars", "double", "simple", "banner"]
    
    for style in styles:
        print(f"\n{style.upper()}:")
        print(ASCIILogoGenerator.generate(text, style))

def main():
    """Pääohjelma / Main program"""
    print("\n" + "=" * 70)
    print("KUITTIKONE - TÄYDELLINEN ESIMERKKI")
    print("RECEIPT PRINTER - COMPLETE EXAMPLE")
    print("=" * 70)
    print("\nTämä esimerkki näyttää kaikki uudet ominaisuudet:")
    print("This example demonstrates all new features:")
    print("  ✓ ASCII-logon generointi / ASCII logo generation")
    print("  ✓ Maksutiedot / Payment information")
    print("  ✓ Muokattavat yritystiedot / Editable company info")
    print("  ✓ Offline-tallennus / Offline storage")
    print("  ✓ Kuittihistoria / Receipt history")
    print("  ✓ Lisähuomiot / Additional notes")
    
    # Luo kuitti
    receipt = create_complete_receipt()
    
    # Näytä kuitti
    display_receipt(receipt)
    
    # Näytä tilastot
    show_statistics(receipt)
    
    # Näytä ASCII-logot
    show_ascii_logos()
    
    print("\n" + "=" * 70)
    print("ESIMERKKI VALMIS! / EXAMPLE COMPLETED!")
    print("=" * 70)
    print("\nKuitit tallennettu kansioon / Receipts saved to:")
    print(f"  {os.path.abspath('kuitit_offline')}")
    print("\nVoit nyt:")
    print("You can now:")
    print("  1. Käynnistää GUI: python receipt_app.py")
    print("     Start GUI: python receipt_app.py")
    print("  2. Käynnistää terminaali: python receipt_app.py --terminal")
    print("     Start terminal: python receipt_app.py --terminal")
    print("  3. Katsoa historiaa: tarkista kuitit_offline/-kansio")
    print("     View history: check kuitit_offline/ directory")
    print("\n")

if __name__ == "__main__":
    main()
