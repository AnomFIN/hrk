#!/usr/bin/env python3
"""
Demo tyylikkaistä ASCII-logoista / Demo of stylish ASCII logos
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from receipt_app import ASCIILogoGenerator

def demo_all_styles():
    """Näytä kaikki logo-tyylit / Show all logo styles"""
    
    print("\n" + "=" * 70)
    print("TYYLIKÄS ASCII LOGO -GENERAATTORI")
    print("STYLISH ASCII LOGO GENERATOR")
    print("=" * 70)
    
    text = "HRK"
    styles = [
        ("box", "Laatikko / Box"),
        ("stars", "Tähdet / Stars"),
        ("double", "Kaksoisreuna / Double"),
        ("banner", "Banneri / Banner"),
        ("fancy", "Koristeellinen / Fancy"),
        ("shadow", "Varjostus / Shadow"),
        ("blocks", "Lohkot / Blocks"),
        ("wave", "Aalto / Wave"),
        ("diamond", "Timantti / Diamond"),
        ("simple", "Yksinkertainen / Simple")
    ]
    
    for style_name, description in styles:
        print(f"\n{'─' * 70}")
        print(f"TYYLI / STYLE: {description}")
        print(f"{'─' * 70}")
        logo = ASCIILogoGenerator.generate(text, style_name)
        print(logo)
    
    print("\n" + "=" * 70)
    print("PITKÄ TEKSTI / LONG TEXT EXAMPLES")
    print("=" * 70)
    
    long_text = "HARJUN RASKASKONE"
    showcase_styles = ["box", "stars", "fancy", "shadow", "diamond"]
    
    for style_name in showcase_styles:
        style_desc = dict(styles)[style_name]
        print(f"\n{style_desc}:")
        logo = ASCIILogoGenerator.generate(long_text, style_name)
        print(logo)

def demo_receipt_with_stylish_logo():
    """Näytä kuitti tyylikkäällä logolla / Show receipt with stylish logo"""
    from receipt_app import Receipt
    
    print("\n" + "=" * 70)
    print("KUITTI TYYLIKKÄÄLLÄ LOGOLLA")
    print("RECEIPT WITH STYLISH LOGO")
    print("=" * 70)
    
    styles_to_test = ["fancy", "shadow", "diamond"]
    
    for style in styles_to_test:
        receipt = Receipt()
        receipt.set_custom_logo("HARJUN RASKASKONE", style)
        receipt.add_product("Testituote", 1, 100.00)
        
        print(f"\n{'═' * 70}")
        print(f"TYYLI: {style.upper()}")
        print(f"{'═' * 70}")
        print(receipt.generate_text())

def main():
    """Pääohjelma / Main program"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  TYYLIKÄS ASCII LOGO -DEMONSTRAATIO".center(68) + "║")
    print("║" + "  STYLISH ASCII LOGO DEMONSTRATION".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print("\nTämä demo näyttää kaikki 10 tyylikästä ASCII-logo-tyyliä:")
    print("This demo shows all 10 stylish ASCII logo styles:")
    print("  1. Box - Perus laatikko / Basic box")
    print("  2. Stars - Koristellut tähdet / Decorated stars")
    print("  3. Double - Kaksoisreuna / Double border")
    print("  4. Banner - Pyöristetty banneri / Rounded banner")
    print("  5. Fancy - Koristeellinen / Fancy decorative")
    print("  6. Shadow - Varjostus / Shadow effect")
    print("  7. Blocks - Lohkokirjaimet / Block letters")
    print("  8. Wave - Aaltoviiva / Wave pattern")
    print("  9. Diamond - Timanttimuoto / Diamond shape")
    print(" 10. Simple - Yksinkertainen / Simple")
    
    demo_all_styles()
    demo_receipt_with_stylish_logo()
    
    print("\n" + "=" * 70)
    print("DEMO VALMIS! / DEMO COMPLETED!")
    print("=" * 70)
    print("\nKaikki logot käyttävät ISOJA KIRJAIMIA tyylikkyyden vuoksi.")
    print("All logos use UPPERCASE letters for stylish appearance.")
    print("\nVoit nyt käyttää näitä tyylejä receipt_app.py:ssä:")
    print("You can now use these styles in receipt_app.py:")
    print("  receipt.set_custom_logo('YOUR TEXT', 'fancy')")
    print()

if __name__ == "__main__":
    main()
