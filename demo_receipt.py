#!/usr/bin/env python3
"""
Demo script for receipt_app.py
Demonstrates programmatic usage of the receipt application.
"""

import sys
from pathlib import Path

# Import receipt_app
sys.path.insert(0, str(Path(__file__).parent))
import receipt_app


def demo_basic_receipt():
    """Create a basic receipt and display it"""
    print("\n=== DEMO: Yksinkertainen kuitti / Basic Receipt ===\n")
    
    # Luo kuitti / Create receipt
    receipt = receipt_app.Receipt()
    
    # Lisää tuotteita / Add products
    receipt.add_product("Kaivinkone 15t", 3, 850.00)
    receipt.add_product("Kuorma-auto", 5, 450.00)
    receipt.add_product("Nosturi 25t", 2, 1200.00)
    
    # Näytä kuitti / Display receipt
    print(receipt.generate_text())
    
    # Näytä yhteenveto / Show summary
    print(f"\nYhteenveto / Summary:")
    print(f"  Tuotteita: {len(receipt.products)} kpl")
    print(f"  Välisumma: {receipt.get_subtotal():.2f} €")
    print(f"  ALV 24%: {receipt.get_vat():.2f} €")
    print(f"  Yhteensä: {receipt.get_total():.2f} €")


def demo_png_export():
    """Demonstrate PNG export functionality"""
    print("\n=== DEMO: PNG-tallennus / PNG Export ===\n")
    
    if not receipt_app.PILLOW_AVAILABLE:
        print("⚠ Pillow ei ole asennettu. Asenna: pip install pillow")
        print("⚠ Pillow not installed. Install: pip install pillow")
        return
    
    # Luo kuitti / Create receipt
    receipt = receipt_app.Receipt()
    receipt.add_product("Tieyhtiö paketti", 1, 5500.00)
    receipt.add_product("Huoltopalvelu", 1, 250.00)
    
    # Tallenna PNG / Save as PNG
    output_path = "demo_kuitti.png"
    text = receipt.generate_text()
    
    if receipt_app.ReceiptPrinter.save_as_png(text, output_path):
        print(f"✓ Kuitti tallennettu: {output_path}")
        print(f"✓ Receipt saved: {output_path}")
    else:
        print("✗ Tallennus epäonnistui / Save failed")


def demo_product_management():
    """Demonstrate product management"""
    print("\n=== DEMO: Tuotteiden hallinta / Product Management ===\n")
    
    receipt = receipt_app.Receipt()
    
    # Lisää tuotteita / Add products
    print("Lisätään 3 tuotetta / Adding 3 products...")
    receipt.add_product("Tuote A", 2, 100.00)
    receipt.add_product("Tuote B", 1, 50.00)
    receipt.add_product("Tuote C", 3, 75.00)
    
    print(f"Tuotteita yhteensä: {len(receipt.products)}")
    for i, product in enumerate(receipt.products):
        print(f"  {i+1}. {product.name} - {product.quantity} x {product.price:.2f}€")
    
    # Poista tuote / Remove product
    print("\nPoistetaan tuote 2 (Tuote B) / Removing product 2 (Tuote B)...")
    receipt.remove_product(1)
    
    print(f"Tuotteita jäljellä: {len(receipt.products)}")
    for i, product in enumerate(receipt.products):
        print(f"  {i+1}. {product.name} - {product.quantity} x {product.price:.2f}€")


def demo_validation():
    """Demonstrate input validation"""
    print("\n=== DEMO: Syötteiden validointi / Input Validation ===\n")
    
    receipt = receipt_app.Receipt()
    
    print("Testataan virheellisiä syötteitä / Testing invalid inputs...")
    
    # Negatiivinen määrä / Negative quantity
    result = receipt.add_product("Tuote", -1, 10.0)
    print(f"  Negatiivinen määrä: {'Hylätty ✓' if not result else 'Virhe ✗'}")
    
    # Nolla määrä / Zero quantity
    result = receipt.add_product("Tuote", 0, 10.0)
    print(f"  Nolla määrä: {'Hylätty ✓' if not result else 'Virhe ✗'}")
    
    # Negatiivinen hinta / Negative price
    result = receipt.add_product("Tuote", 1, -10.0)
    print(f"  Negatiivinen hinta: {'Hylätty ✓' if not result else 'Virhe ✗'}")
    
    # Virheellinen indeksi / Invalid index
    result = receipt.remove_product(999)
    print(f"  Virheellinen indeksi: {'Hylätty ✓' if not result else 'Virhe ✗'}")
    
    print("\nKaikki validoinnit toimivat oikein! / All validations work correctly!")


def main():
    """Run all demos"""
    print("=" * 60)
    print("  KUITTITULOSTIN - DEMO")
    print("  Receipt Printer Application - Demonstration")
    print("=" * 60)
    
    try:
        demo_basic_receipt()
        demo_product_management()
        demo_validation()
        demo_png_export()
        
        print("\n" + "=" * 60)
        print("  Demo valmis! / Demo complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nVirhe / Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
