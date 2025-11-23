#!/usr/bin/env python3
"""
Demo kuittipohjan tallennuksesta ja latauksesta
Demo of receipt template save and load functionality
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from receipt_app import Receipt, TemplateManager

def demo_template_system():
    """Demonstroi pohjan tallennusta ja latausta"""
    
    print("\n" + "=" * 70)
    print("KUITTIPOHJAN HALLINTAJÄRJESTELMÄ")
    print("RECEIPT TEMPLATE MANAGEMENT SYSTEM")
    print("=" * 70)
    
    # Luo template manager
    template_manager = TemplateManager()
    
    # Luo esimerkki kuitti 1: Rakennusalan yritys
    print("\n[1/5] Luodaan esimerkki kuitti - Rakennusalan yritys...")
    receipt1 = Receipt()
    receipt1.update_company_info(
        name="Rakennus Oy ABC",
        business_id="FI11111111",
        address="Rakennustie 1, 00100 Helsinki",
        phone="+358 40 111 1111",
        email="info@rakennusabc.fi",
        website="www.rakennusabc.fi"
    )
    receipt1.set_custom_logo("RAKENNUS ABC", "fancy")
    receipt1.set_payment_info("Lasku / Invoice", "", "", "RF123456")
    receipt1.receipt_notes = "Maksuehdot: 14 päivää netto"
    
    # Tallenna pohja 1
    print("[2/5] Tallennetaan pohja 'rakennusalan_kuitti'...")
    if template_manager.save_template(receipt1, "rakennusalan_kuitti"):
        print("     ✓ Pohja tallennettu!")
    
    # Luo esimerkki kuitti 2: Kahvila
    print("\n[3/5] Luodaan toinen esimerkki - Kahvila...")
    receipt2 = Receipt()
    receipt2.update_company_info(
        name="Kahvila Helmi",
        business_id="FI22222222",
        address="Keskuskatu 5, 00200 Helsinki",
        phone="+358 50 222 2222",
        email="info@kahvilahelmi.fi",
        website="www.kahvilahelmi.fi"
    )
    receipt2.set_custom_logo("KAHVILA HELMI", "stars")
    receipt2.set_payment_info("Kortti / Card", "Visa", "", "")
    receipt2.receipt_notes = "Tervetuloa uudelleen!"
    
    # Tallenna pohja 2
    print("[4/5] Tallennetaan pohja 'kahvilan_kuitti'...")
    if template_manager.save_template(receipt2, "kahvilan_kuitti"):
        print("     ✓ Pohja tallennettu!")
    
    # Listaa pohjat
    print("\n[5/5] Listataan kaikki tallennetut pohjat...")
    templates = template_manager.list_templates()
    print(f"     Tallennetut pohjat ({len(templates)} kpl):")
    for template in templates:
        print(f"       • {template}")
    
    # Lataa ja näytä pohja
    print("\n" + "=" * 70)
    print("POHJAN LATAUS JA KÄYTTÖ")
    print("LOADING AND USING TEMPLATE")
    print("=" * 70)
    
    print("\nLadataan pohja 'rakennusalan_kuitti'...")
    loaded_receipt = template_manager.load_template("rakennusalan_kuitti")
    
    if loaded_receipt:
        print("✓ Pohja ladattu!")
        print("\nLadatut tiedot:")
        print(f"  Yritys: {loaded_receipt.company_info['name']}")
        print(f"  Y-tunnus: {loaded_receipt.company_info['business_id']}")
        print(f"  Maksutapa: {loaded_receipt.payment_info['method']}")
        print(f"  Logo-tyyli: {loaded_receipt.logo_style}")
        print(f"  Huomiot: {loaded_receipt.receipt_notes}")
        
        # Lisää tuotteita
        print("\nLisätään tuotteita ladattuun pohjaan...")
        loaded_receipt.add_product("Työtunnit", 8, 50.00)
        loaded_receipt.add_product("Materiaalit", 1, 250.00)
        
        # Generoi kuitti
        print("\n" + "=" * 70)
        print("VALMIS KUITTI POHJALLA")
        print("COMPLETED RECEIPT WITH TEMPLATE")
        print("=" * 70)
        receipt_text = loaded_receipt.generate_text()
        print(receipt_text)
    
    # Pohjan tietojen haku
    print("\n" + "=" * 70)
    print("POHJAN TIEDOT")
    print("TEMPLATE INFORMATION")
    print("=" * 70)
    
    for template_name in templates:
        info = template_manager.get_template_info(template_name)
        if info:
            print(f"\nPohja: {template_name}")
            print(f"  Luotu: {info.get('created', 'N/A')}")
            print(f"  Yritys: {info.get('company_info', {}).get('name', 'N/A')}")
            print(f"  Logo: {info.get('logo_style', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("DEMO VALMIS!")
    print("DEMO COMPLETED!")
    print("=" * 70)
    print("\nOminaisuudet / Features:")
    print("  ✓ Tallenna kuittipohja ilman tuotteita")
    print("  ✓ Lataa pohja ja lisää tuotteita")
    print("  ✓ Säilytä yritystiedot, maksutiedot, logo ja huomiot")
    print("  ✓ Listaa ja hallitse pohjia")
    print("  ✓ Poista vanhoja pohjia")
    print("\nTallennettu kansioon: kuitti_pohjat/")
    print()

def main():
    """Pääohjelma"""
    print("\n╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "KUITTIPOHJAN HALLINTA - DEMO".center(68) + "║")
    print("║" + "RECEIPT TEMPLATE MANAGEMENT - DEMO".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    demo_template_system()

if __name__ == "__main__":
    main()
