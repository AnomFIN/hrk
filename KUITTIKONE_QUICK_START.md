# Kuittikone Quick Start Guide

**Get started with kuittikone in 5 minutes!**

## 🚀 Installation

```bash
# No installation needed - pure Python!
# Just copy the file:
cp kuittikone.py /your/project/
```

## ⚡ Quick Examples

### 1. Basic Receipt (30 seconds)

```python
from kuittikone import KuittikoneManager, PaymentMethod, CardType

# Create manager
manager = KuittikoneManager()

# Add default presets
from kuittikone import create_default_presets
for preset in create_default_presets():
    manager.add_company_preset(preset)

# Switch to HRK preset
manager.switch_preset("hrk_default")

# Generate receipt
products = [
    {"name": "Product 1", "quantity": 2, "price": 10.00},
    {"name": "Product 2", "quantity": 1, "price": 25.00}
]

receipt = manager.generate_receipt(
    products=products,
    payment_method=PaymentMethod.CARD,
    card_type=CardType.VISA
)

print(receipt)
```

### 2. Add Your Company (1 minute)

```python
from kuittikone import CompanyPreset, TemplateType

my_company = CompanyPreset(
    preset_id="my_company",
    company_name="My Company Oy",
    business_id="FI12345678",
    address="Street 1, City",
    phone="+358 40 123 4567",
    email="info@mycompany.com",
    template_type=TemplateType.CORPORATE,
    footer_text="Thank you for your business!"
)

manager.add_company_preset(my_company)
manager.switch_preset("my_company")
```

### 3. Add Warranty Tracking (2 minutes)

```python
from kuittikone import WarrantyInfo
from datetime import datetime

warranty = WarrantyInfo(
    serial_number="SN-2025-001",
    purchase_date=datetime.now().isoformat(),
    warranty_months=24,
    product_name="Product Name",
    return_days=30
)

manager.add_warranty(warranty)

# Include in receipt
receipt = manager.generate_receipt(
    products=products,
    payment_method=PaymentMethod.CARD,
    serial_numbers=["SN-2025-001"]
)
```

### 4. Add Promotional Rule (2 minutes)

```python
from kuittikone import PromoRule

# Get current preset
preset = manager.get_current_preset()

# Add promo
promo = PromoRule(
    rule_id="spring_sale",
    description="Spring sale over 50€",
    condition_type="amount_over",
    condition_value=50.0,
    action_type="add_line",
    action_value="🌸 Spring Sale: -15% on next purchase!"
)

preset.promo_rules.append(promo)
manager.add_company_preset(preset)
```

### 5. Configure Payment Cards (2 minutes)

```python
from kuittikone import PaymentCardPreset, CardType

preset = manager.get_current_preset()

# Add Amex with fee
amex = PaymentCardPreset(
    card_type=CardType.AMEX,
    enabled=True,
    name="American Express",
    fee_percentage=2.5,
    icon="💎"
)

preset.payment_presets.append(amex)
manager.add_company_preset(preset)
```

### 6. Backup to USB (30 seconds)

```python
# Backup everything
manager.backup_to_usb("/media/usb/backups")

# Restore from backup
manager.restore_from_usb("/media/usb/backups/kuittikone_backup_20251118_120000.json")
```

## 🎨 Templates

Switch receipt styles instantly:

```python
from kuittikone import TemplateType

preset = manager.get_current_preset()

# Choose template
preset.template_type = TemplateType.MINIMAL  # Simple receipt
# preset.template_type = TemplateType.CORPORATE  # Full branding
# preset.template_type = TemplateType.COMPACT  # Space-efficient
# preset.template_type = TemplateType.PROMO  # Promotion-focused

manager.add_company_preset(preset)
```

## 🎭 ASCII Logos

Create ASCII art logos:

```python
from kuittikone import ASCIILogoEncoder

# Generate logo
logo = ASCIILogoEncoder.text_to_ascii_art("MY COMPANY", "block")
print(logo)
# Output:
# ╔════════════╗
# ║ MY COMPANY ║
# ╚════════════╝

# For thermal printers (EPSON ESC/POS)
escpos = ASCIILogoEncoder.to_epson_escpos("LOGO", alignment="center")
```

## 🔤 Font Styles

Apply different fonts to receipt sections:

```python
from kuittikone import ReceiptLayout, FontStyle

preset = manager.get_current_preset()

preset.layout = ReceiptLayout(
    header_font=FontStyle.BOLD_BIG,     # Large header
    product_font=FontStyle.NORMAL,       # Standard products
    footer_font=FontStyle.SLIM          # Compact footer
)

manager.add_company_preset(preset)
```

**Available Fonts**: SLIM, BLOCK, ASCII_RETRO, BOLD_BIG, DOUBLE_WIDTH, PIXEL_TIGHT, NORMAL

## 📋 Common Tasks

### List All Companies

```python
for preset in manager.list_presets():
    print(f"{preset.preset_id}: {preset.company_name}")
```

### Delete Company

```python
manager.delete_preset("company_id")
```

### Get Current Company

```python
current = manager.get_current_preset()
print(f"Active: {current.company_name}")
```

### Check Warranty

```python
warranty = manager.get_warranty("SN-2025-001")
if warranty and warranty.is_warranty_valid():
    print("✓ Warranty is valid")
```

### Custom Layout

```python
from kuittikone import ReceiptLayout

layout = ReceiptLayout(
    show_logo=True,
    show_header=True,
    show_products=True,
    show_totals=True,
    show_vat_breakdown=True,
    show_footer=True,
    show_warranty=True,
    show_promo=True,
    extra_lines_before_products=1,
    extra_lines_after_totals=2
)

preset.layout = layout
manager.add_company_preset(preset)
```

## 🔧 Configuration

Configuration is stored in `kuittikone_config.json` and automatically created on first run.

### Manual Edit

```json
{
  "version": "1.0.0",
  "presets": { ... },
  "warranty_database": { ... },
  "settings": {
    "default_receipt_width": 50,
    "enable_offline_logging": true,
    "backup_directory": "./backups"
  }
}
```

## 🧪 Testing

```bash
# Run demo
python kuittikone.py

# Run all tests
python -m unittest test_kuittikone -v

# Run integration demo
python demo_kuittikone_integration.py
```

## 📚 Full Documentation

For complete documentation, see:
- **KUITTIKONE_README.md** - Full feature documentation
- **KUITTIKONE_IMPLEMENTATION_SUMMARY.md** - Implementation details

## 🆘 Help

### Common Issues

**"No preset selected"**
```python
# Solution: Add and switch to a preset
manager.add_company_preset(preset)
manager.switch_preset("preset_id")
```

**"Warranty not found"**
```python
# Solution: Add warranty first
manager.add_warranty(warranty)
```

**"Receipt too wide"**
```python
# Solution: Adjust width in settings
manager.config["settings"]["default_receipt_width"] = 42
manager._save_config()
```

## 🎯 Next Steps

1. ✅ Read **KUITTIKONE_README.md** for all features
2. ✅ Run `python kuittikone.py` to see demo
3. ✅ Run `python demo_kuittikone_integration.py` for examples
4. ✅ Create your first company preset
5. ✅ Generate your first receipt
6. ✅ Add warranty tracking
7. ✅ Set up promotional rules
8. ✅ Configure payment cards
9. ✅ Customize receipt layout
10. ✅ Backup to USB

## 📞 Support

For questions or issues:
- Check the demos: `demo_kuittikone_integration.py`
- Run tests: `python -m unittest test_kuittikone -v`
- Review examples in `KUITTIKONE_README.md`

---

**Ready to start? Run:** `python kuittikone.py` 🚀
