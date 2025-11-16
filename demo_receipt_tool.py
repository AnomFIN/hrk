#!/usr/bin/env python3
"""
Demo script for receipt_tool.py
Shows all features in action
"""

from receipt_tool import Receipt, ReceiptExporter
from datetime import datetime
import os

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "RECEIPT TOOL DEMO" + " " * 31 + "║")
    print("║" + " " * 15 + "Harjun Raskaskone Oy (HRK)" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Feature 1: Basic receipt with default template
    print_section("1. Basic Receipt with Default Template")
    r1 = Receipt()
    r1.add_product("Kaivinkone 15t - Weekly Rental", 1, 850.00)
    r1.add_product("Transportation", 2, 125.50)
    r1.add_product("Insurance", 1, 50.00)
    
    print("Products added:")
    for i, p in enumerate(r1.products, 1):
        print(f"  {i}. {p.name} - {p.quantity} x {p.price:.2f}€")
    
    print(f"\nSubtotal: {r1.get_subtotal():.2f}€")
    print(f"VAT (24%): {r1.get_vat():.2f}€")
    print(f"Total: {r1.get_total():.2f}€")
    
    # Save to file
    filename1 = f"/tmp/demo_default_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    ReceiptExporter.export_txt(r1, filename1)
    print(f"\n✓ Saved to: {filename1}")
    
    # Feature 2: Minimal template
    print_section("2. Receipt with Minimal Template")
    r2 = Receipt()
    r2.current_template = "minimal"
    r2.add_product("Nosturi 20t", 1, 1200.00)
    r2.add_product("Operator", 8, 45.00)
    
    print("Template: Minimal")
    print(f"Total: {r2.get_total():.2f}€")
    
    filename2 = f"/tmp/demo_minimal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    ReceiptExporter.export_txt(r2, filename2)
    print(f"✓ Saved to: {filename2}")
    
    # Feature 3: Custom logo
    print_section("3. Custom ASCII Logo")
    r3 = Receipt()
    
    custom_logo = """
    ╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
    ┃  🏗️  HARJUN RASKASKONE OY  🏗️      ┃
    ┃     Professional Equipment         ┃
    ┃        Rental Service              ┃
    ╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
    """.strip()
    
    r3.set_logo(custom_logo)
    r3.add_product("Premium Excavator", 1, 1500.00)
    
    print("Custom logo applied!")
    print(f"Total: {r3.get_total():.2f}€")
    
    filename3 = f"/tmp/demo_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    ReceiptExporter.export_txt(r3, filename3)
    print(f"✓ Saved to: {filename3}")
    
    # Feature 4: Manual override
    print_section("4. Manual Text Override")
    r4 = Receipt()
    r4.add_product("Test Item", 1, 100.00)
    
    override_text = """
    ╔═══════════════════════════════════════╗
    ║        CUSTOM RECEIPT                 ║
    ╚═══════════════════════════════════════╝
    
    This receipt has been manually edited
    to show custom content.
    
    Special Instructions:
    - Handle with care
    - Contact office for pickup
    
    Thank you for your business!
    """
    
    r4.set_manual_override(override_text.strip())
    
    print("Manual override applied!")
    print("Receipt now shows custom text instead of generated content")
    
    filename4 = f"/tmp/demo_override_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    ReceiptExporter.export_txt(r4, filename4)
    print(f"✓ Saved to: {filename4}")
    
    # Feature 5: History
    print_section("5. Receipt History")
    r1.save_to_history()
    r2.save_to_history()
    r3.save_to_history()
    
    print("✓ 3 receipts saved to history")
    print(f"History is stored in: receipt_tool.json")
    
    # Feature 6: Control character cleanup
    print_section("6. Control Character Cleanup")
    r5 = Receipt()
    text_with_controls = "Test\x00Product\x01Name\nWith\tTabs"
    cleaned = r5._cleanup_text(text_with_controls)
    
    print("Original (with control chars):")
    print(f"  {repr(text_with_controls)}")
    print("\nCleaned (safe for display):")
    print(f"  {repr(cleaned)}")
    print(f"  Result: {cleaned}")
    
    # Summary
    print_section("✨ DEMO SUMMARY")
    print("Created 4 receipts demonstrating:")
    print("  ✓ Default template")
    print("  ✓ Minimal template")
    print("  ✓ Custom ASCII logo")
    print("  ✓ Manual text override")
    print("  ✓ Receipt history")
    print("  ✓ Control character cleanup")
    
    print("\nFiles created:")
    for filename in [filename1, filename2, filename3, filename4]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  • {filename} ({size} bytes)")
    
    print("\nNext steps:")
    print("  1. View the files: cat /tmp/demo_*.txt")
    print("  2. Try the GUI: python3 receipt_tool.py")
    print("  3. Run smoke test: python3 receipt_tool.py --smoke-test")
    print("  4. Edit logo: python3 receipt_tool.py --edit-logo")
    print("  5. Get help: python3 receipt_tool.py --help")
    
    print("\n" + "=" * 70)
    print("Demo completed successfully! 🎉")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
