#!/usr/bin/env python3
"""
Demo uusista kuittikone-ominaisuuksista / Demo of new kuittikone features
"""

import sys
import os

# Lisää moduulipolku
sys.path.insert(0, os.path.dirname(__file__))

from receipt_app import Receipt, ASCIILogoGenerator, OfflineStorage

def demo_ascii_logo():
    """Demonstroi ASCII-logon generointia"""
    print("\n" + "=" * 60)
    print("DEMO 1: ASCII Logo Generator")
    print("=" * 60)
    
    text = "HRK"
    styles = ["box", "stars", "double", "simple", "banner"]
    
    for style in styles:
        print(f"\nTyyli / Style: {style}")
        print(ASCIILogoGenerator.generate(text, style))

def demo_payment_info():
    """Demonstroi maksutietojen lisäystä"""
    print("\n" + "=" * 60)
    print("DEMO 2: Maksutietojen lisäys / Payment Information")
    print("=" * 60)
    
    receipt = Receipt()
    receipt.add_product("Kaivinkone 15t", 1, 850.00)
    
    # Lisää maksutiedot
    receipt.set_payment_info(
        method="Kortti / Card",
        card_type="Visa Debit",
        transaction_id="TX-2024-001234",
        bank_reference="RF1234567890"
    )
    
    print("\nKuitti maksutiedoilla / Receipt with payment info:")
    print(receipt.generate_text())

def demo_custom_logo():
    """Demonstroi mukautetun logon käyttöä"""
    print("\n" + "=" * 60)
    print("DEMO 3: Mukautettu ASCII-logo / Custom ASCII Logo")
    print("=" * 60)
    
    receipt = Receipt()
    receipt.set_custom_logo("HARJUN RASKASKONE", "box")
    receipt.add_product("Testituote", 1, 10.00)
    
    print("\nKuitti mukautetulla logolla / Receipt with custom logo:")
    print(receipt.generate_text())

def demo_offline_storage():
    """Demonstroi offline-tallennusta"""
    print("\n" + "=" * 60)
    print("DEMO 4: Offline-tallennus / Offline Storage")
    print("=" * 60)
    
    storage = OfflineStorage()
    
    # Luo testkuitti
    receipt = Receipt()
    receipt.add_product("Kuorma-auto", 2, 450.00)
    receipt.add_product("Kaivinkone", 1, 850.00)
    receipt.set_payment_info("Käteinen / Cash")
    receipt.receipt_notes = "Testihum: Toimitus huomenna / Test note: Delivery tomorrow"
    
    # Tallenna
    if storage.save_receipt(receipt):
        print(f"\n✓ Kuitti tallennettu offline-tilaan!")
        print(f"  Tallennuskansio / Storage directory: {storage.storage_dir}")
        
        # Näytä historia
        history = storage.load_history()
        print(f"\n  Historiassa kuitteja / Receipts in history: {len(history)}")
        
        if history:
            print("\n  Viimeisin kuitti / Latest receipt:")
            latest = history[-1]
            print(f"    - Aikaleima / Timestamp: {latest.get('timestamp')}")
            print(f"    - Yritys / Company: {latest.get('company')}")
            print(f"    - Summa / Total: {latest.get('total'):.2f} €")
            print(f"    - Tiedosto / File: {latest.get('filename')}")
        
        # Lista tiedostoja
        files = storage.list_receipts()
        print(f"\n  Tallennetut tiedostot / Saved files: {len(files)}")
        for f in files[:3]:  # Näytä max 3
            print(f"    - {f}")
    else:
        print("✗ Tallennus epäonnistui / Save failed!")

def demo_editable_info():
    """Demonstroi muokattavia tietoja"""
    print("\n" + "=" * 60)
    print("DEMO 5: Muokattavat yritystiedot / Editable Company Info")
    print("=" * 60)
    
    receipt = Receipt()
    
    # Päivitä yritystiedot
    receipt.update_company_info(
        name="Uusi Yritysnimi Oy",
        business_id="FI99887766",
        address="Uusi Osoite 123, 00200 Helsinki",
        phone="+358 50 999 8888",
        email="info@uusiyritys.fi",
        website="www.uusiyritys.fi"
    )
    
    receipt.add_product("Testituote", 1, 100.00)
    
    print("\nKuitti päivitetyillä tiedoilla / Receipt with updated info:")
    print(receipt.generate_text())

def main():
    """Pääohjelma / Main program"""
    print("\n" + "=" * 60)
    print("KUITTIKONE - UUDET OMINAISUUDET")
    print("RECEIPT PRINTER - NEW FEATURES")
    print("=" * 60)
    
    # Suorita demot
    demo_ascii_logo()
    demo_payment_info()
    demo_custom_logo()
    demo_offline_storage()
    demo_editable_info()
    
    print("\n" + "=" * 60)
    print("KAIKKI DEMOT SUORITETTU! / ALL DEMOS COMPLETED!")
    print("=" * 60)
    print("\nUudet ominaisuudet / New features:")
    print("✓ ASCII-logon generointi / ASCII logo generation")
    print("✓ Maksutietojen lisäys / Payment information")
    print("✓ Mukautettu logo / Custom logo")
    print("✓ Offline-tallennus / Offline storage")
    print("✓ Muokattavat yritystiedot / Editable company info")
    print("✓ Kuittihistoria / Receipt history")
    print("✓ Lisähuomiot / Additional notes")
    print()

if __name__ == "__main__":
    main()
