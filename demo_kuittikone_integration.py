#!/usr/bin/env python3
"""
Demo: Integration between kuittikone and receipt_tool

This demonstrates how the advanced kuittikone features can work
alongside the existing receipt_tool.py for enhanced functionality.
"""

import sys
from datetime import datetime

# Import both systems
import kuittikone
import receipt_tool


def demo_standalone_kuittikone():
    """Demo 1: Kuittikone standalone with all advanced features"""
    print("\n" + "=" * 70)
    print("DEMO 1: Kuittikone Standalone - All Advanced Features")
    print("=" * 70)
    
    # Initialize kuittikone
    manager = kuittikone.KuittikoneManager()
    
    # Add company presets
    for preset in kuittikone.create_default_presets():
        manager.add_company_preset(preset)
    
    print("\n✓ Loaded company presets:")
    for preset in manager.list_presets():
        print(f"  - {preset.company_name} ({preset.preset_id})")
    
    # Switch to HRK preset
    manager.switch_preset("hrk_default")
    current = manager.get_current_preset()
    print(f"\n✓ Active preset: {current.company_name}")
    
    # Add warranty
    warranty = kuittikone.WarrantyInfo(
        serial_number="HRK-DEMO-2025-001",
        purchase_date=datetime.now().isoformat(),
        warranty_months=12,
        product_name="Kaivinkone 15t",
        return_days=14,
        notes="Demo warranty record"
    )
    manager.add_warranty(warranty)
    print(f"✓ Added warranty: {warranty.serial_number}")
    
    # Generate advanced receipt
    products = [
        {"name": "Kaivinkone 15t", "quantity": 1, "price": 850.00},
        {"name": "Nosturi 20m", "quantity": 1, "price": 1200.00}
    ]
    
    receipt = manager.generate_receipt(
        products=products,
        payment_method=kuittikone.PaymentMethod.CARD,
        card_type=kuittikone.CardType.VISA,
        serial_numbers=["HRK-DEMO-2025-001"]
    )
    
    print("\n" + "─" * 70)
    print("GENERATED RECEIPT (with warranty & promo):")
    print("─" * 70)
    print(receipt)
    print("─" * 70)


def demo_receipt_tool_basic():
    """Demo 2: Basic receipt_tool.py functionality"""
    print("\n" + "=" * 70)
    print("DEMO 2: Receipt Tool - Basic Template System")
    print("=" * 70)
    
    # Initialize receipt_tool
    receipt = receipt_tool.Receipt()
    
    print("\n✓ Available templates:")
    for template_id, template_data in receipt.config.get("templates", {}).items():
        print(f"  - {template_id}: {template_data.get('name', 'Unknown')}")
    
    # Add products
    receipt.add_product("Kuorma-auto", 2, 450.00)
    receipt.add_product("Perävaunuvuokra", 1, 350.00)
    print("\n✓ Added products to receipt")
    
    # Generate receipt
    receipt_text = receipt.generate_text()
    
    print("\n" + "─" * 70)
    print("GENERATED RECEIPT (basic template):")
    print("─" * 70)
    print(receipt_text)
    print("─" * 70)


def demo_hybrid_approach():
    """Demo 3: Hybrid approach - Use kuittikone for config, receipt_tool for output"""
    print("\n" + "=" * 70)
    print("DEMO 3: Hybrid Approach - Best of Both Worlds")
    print("=" * 70)
    
    # Use kuittikone for company management
    km = kuittikone.KuittikoneManager()
    
    # Create a custom company preset
    custom_preset = kuittikone.CompanyPreset(
        preset_id="hybrid_demo",
        company_name="Hybrid Demo Oy",
        business_id="FI99999999",
        address="Demo Street 123, Helsinki",
        phone="+358 40 999 9999",
        email="demo@hybrid.fi",
        template_type=kuittikone.TemplateType.CORPORATE,
        slogan="Best of Both Worlds",
        footer_text="Powered by Kuittikone + Receipt Tool"
    )
    km.add_company_preset(custom_preset)
    km.switch_preset("hybrid_demo")
    
    print(f"\n✓ Using kuittikone preset: {custom_preset.company_name}")
    
    # Get company info from kuittikone
    preset = km.get_current_preset()
    
    # Create receipt_tool receipt with kuittikone company info
    receipt = receipt_tool.Receipt()
    receipt.company_info = {
        "name": preset.company_name,
        "business_id": preset.business_id,
        "address": preset.address,
        "phone": preset.phone,
        "email": preset.email
    }
    receipt.vat_rate = preset.vat_rate
    
    print("✓ Applied company info to receipt_tool")
    
    # Add products
    receipt.add_product("Hybrid Product 1", 1, 100.00)
    receipt.add_product("Hybrid Product 2", 2, 50.00)
    
    # Generate with receipt_tool
    receipt_text = receipt.generate_text()
    
    print("\n" + "─" * 70)
    print("HYBRID RECEIPT:")
    print("─" * 70)
    print(receipt_text)
    print("─" * 70)


def demo_payment_card_features():
    """Demo 4: Advanced payment card features"""
    print("\n" + "=" * 70)
    print("DEMO 4: Advanced Payment Card Features")
    print("=" * 70)
    
    manager = kuittikone.KuittikoneManager()
    
    # Create preset with specific card configurations
    preset = kuittikone.CompanyPreset(
        preset_id="card_demo",
        company_name="Card Demo Oy",
        business_id="FI88888888",
        address="Card Street 1",
        phone="+358 40 888 8888",
        email="cards@demo.fi"
    )
    
    # Configure card presets
    preset.payment_presets = [
        kuittikone.PaymentCardPreset(
            card_type=kuittikone.CardType.VISA,
            enabled=True,
            name="Visa",
            fee_percentage=0.0,
            description="Standard Visa cards",
            icon="💳"
        ),
        kuittikone.PaymentCardPreset(
            card_type=kuittikone.CardType.AMEX,
            enabled=True,
            name="American Express",
            fee_percentage=2.5,
            description="Amex with 2.5% fee",
            icon="💎"
        )
    ]
    
    manager.add_company_preset(preset)
    manager.switch_preset("card_demo")
    
    print("\n✓ Configured payment cards:")
    for card in preset.payment_presets:
        status = "✓ Enabled" if card.enabled else "✗ Disabled"
        fee_text = f" ({card.fee_percentage}% fee)" if card.fee_percentage > 0 else ""
        print(f"  {card.icon} {card.name}{fee_text} - {status}")
    
    # Generate receipts with different cards
    products = [{"name": "Test Product", "quantity": 1, "price": 100.00}]
    
    print("\n" + "─" * 70)
    print("RECEIPT WITH VISA (0% fee):")
    print("─" * 70)
    receipt_visa = manager.generate_receipt(
        products=products,
        payment_method=kuittikone.PaymentMethod.CARD,
        card_type=kuittikone.CardType.VISA
    )
    print(receipt_visa)
    
    print("\n" + "─" * 70)
    print("RECEIPT WITH AMEX (2.5% fee):")
    print("─" * 70)
    receipt_amex = manager.generate_receipt(
        products=products,
        payment_method=kuittikone.PaymentMethod.CARD,
        card_type=kuittikone.CardType.AMEX
    )
    print(receipt_amex)


def demo_ascii_logo_encoding():
    """Demo 5: ASCII logo encoding for thermal printers"""
    print("\n" + "=" * 70)
    print("DEMO 5: ASCII Logo Encoding for Thermal Printers")
    print("=" * 70)
    
    test_texts = [
        ("HRK", "normal"),
        ("COMPANY", "block"),
        ("SALE!", "banner")
    ]
    
    print("\n✓ Generated ASCII logos:")
    for text, style in test_texts:
        print(f"\n{style.upper()} style for '{text}':")
        logo = kuittikone.ASCIILogoEncoder.text_to_ascii_art(text, style)
        print(logo)
    
    # ESC/POS example
    print("\n✓ EPSON ESC/POS command example:")
    print("  (Shows control characters for thermal printer)")
    escpos = kuittikone.ASCIILogoEncoder.to_epson_escpos("KUITTIKONE", alignment="center")
    print(f"  Length: {len(escpos)} bytes")
    print(f"  Contains ESC commands: {'Yes' if '\\x1B' in repr(escpos) else 'No'}")


def demo_font_engine():
    """Demo 6: Font engine demonstration"""
    print("\n" + "=" * 70)
    print("DEMO 6: Font Engine - Multiple Font Styles")
    print("=" * 70)
    
    test_text = "DEMO TEXT"
    
    print("\n✓ Available font styles:")
    for font_style in kuittikone.FontStyle:
        print(f"\n{font_style.value.upper()}:")
        styled = kuittikone.FontEngine.apply_font(test_text, font_style)
        print(styled)
        
        # Show font info
        info = kuittikone.FontEngine.get_font_info(font_style)
        print(f"  Info: width={info['char_width']}, height={info['line_height']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print(" KUITTIKONE + RECEIPT_TOOL INTEGRATION DEMO")
    print("=" * 70)
    print("\nThis demo showcases:")
    print("  1. Kuittikone standalone (all advanced features)")
    print("  2. Receipt Tool basic functionality")
    print("  3. Hybrid approach (using both systems)")
    print("  4. Advanced payment card features")
    print("  5. ASCII logo encoding")
    print("  6. Font engine demonstration")
    
    try:
        demo_standalone_kuittikone()
        demo_receipt_tool_basic()
        demo_hybrid_approach()
        demo_payment_card_features()
        demo_ascii_logo_encoding()
        demo_font_engine()
        
        print("\n" + "=" * 70)
        print("✓ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nKey Takeaways:")
        print("  • Kuittikone provides 13 advanced offline features")
        print("  • Receipt Tool offers simple template-based receipts")
        print("  • Both can be used together for maximum flexibility")
        print("  • All features work offline without network")
        print("  • Full ESC/POS support for thermal printers")
        print()
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
