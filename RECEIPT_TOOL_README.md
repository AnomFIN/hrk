# Receipt Tool - Kuittityökalu

Advanced receipt editor with ASCII logo support for Harjun Raskaskone Oy (HRK).

## ✨ Features

### Core Features (22/22 Implemented)
1. ✅ **ASCII Logo Editor** - Edit logos in GUI and terminal
2. ✅ **Full Receipt Editor** - Edit complete receipt text with manual override
3. ✅ **Real-time Preview** - Fixed-width panel showing receipt preview
4. ✅ **Configuration System** - JSON-based config (`receipt_tool.json`)
5. ✅ **CLI Flags** - `--edit`, `--edit-logo`, `--preview`, `--save-txt`, `--export-pdf`
6. ✅ **Config Options** - logo, width, VAT, company_info, templates
7. ✅ **Terminal Editor** - Uses `$EDITOR` environment variable (fallback to nano)
8. ✅ **Preview in Console** - Fixed-width console preview
9. ✅ **PDF Export** - Optional reportlab dependency with clear messaging
10. ✅ **TXT Export** - Required, always available
11. ✅ **Logo Validation** - Max line width validation
12. ✅ **Control Character Cleanup** - Removes \x00-\x1f except \n, \t
13. ✅ **GUI Buttons** - Edit Logo, Edit Receipt, Preview, Save, Export PDF
14. ✅ **GUI Dialogs** - OK/Cancel with messageboxes
15. ✅ **Manual Override** - `_manual_override_text` in Receipt class
16. ✅ **Override in generation** - `generate_text()` uses override when set
17. ✅ **Smoke Test** - `--smoke-test` generates demo receipt
18. ✅ **Smoke Test Validation** - Creates demo .txt and attempts PDF export
19. ✅ **Single-file Implementation** - All in `receipt_tool.py`
20. ✅ **Git/PR Friendly** - Clear stdout, easy commit & merge
21. ✅ **Receipt History** - Browse previously saved receipts
22. ✅ **Template System** - Select, add, and modify receipt templates

## 🚀 Quick Start

### Installation

```bash
# Required dependencies
python3 -m pip install tkinter  # For GUI (may be pre-installed)

# Optional dependencies
python3 -m pip install reportlab  # For PDF export
python3 -m pip install pillow     # For advanced image handling
```

### Usage Examples

```bash
# Show help
python3 receipt_tool.py --help

# Launch GUI (default)
python3 receipt_tool.py
python3 receipt_tool.py --gui

# Terminal mode with preview
python3 receipt_tool.py --preview

# Edit ASCII logo in terminal
python3 receipt_tool.py --edit-logo

# Edit full receipt text
python3 receipt_tool.py --edit

# Save as TXT
python3 receipt_tool.py --save-txt receipt.txt

# Export as PDF
python3 receipt_tool.py --export-pdf receipt.pdf

# Combine multiple operations
python3 receipt_tool.py --preview --save-txt output.txt

# Run smoke test
python3 receipt_tool.py --smoke-test
```

## 🎨 GUI Interface

The GUI provides a beautiful, modern interface with:

### Layout
- **Left Panel**: Controls and product management
  - Template selector (radio buttons)
  - Product entry form (name, quantity, price)
  - Shopping cart with listbox
  - Action buttons
- **Right Panel**: Real-time preview
  - Fixed-width font display
  - Scrollable text area
  - Shows current receipt with all formatting

### Color Scheme
- Primary: `#2c3e50` (dark blue-gray)
- Secondary: `#34495e` (medium gray)
- Accent Blue: `#3498db`
- Accent Green: `#27ae60`
- Accent Purple: `#9b59b6`
- Accent Red: `#e74c3c`

### Action Buttons
1. 🎨 **Edit Logo** - Opens dialog to edit ASCII logo
2. ✏️ **Edit Receipt** - Opens dialog to edit full receipt text
3. 💾 **Save TXT** - Export receipt to text file
4. 📄 **Export PDF** - Export receipt to PDF (requires reportlab)
5. 📜 **History** - Browse previously saved receipts

## ⚙️ Configuration

Configuration is stored in `receipt_tool.json` with the following structure:

```json
{
  "logo_ascii": "ASCII logo here",
  "width": 50,
  "vat_rate": 0.24,
  "company_info": {
    "name": "Harjun Raskaskone Oy",
    "business_id": "FI12345678",
    "address": "Teollisuustie 1, 00100 Helsinki",
    "phone": "+358 40 123 4567",
    "email": "info@hrk.fi"
  },
  "templates": {
    "default": {
      "name": "Oletus / Default",
      "logo": "ASCII logo",
      "header_format": "{name}\nY-tunnus: {business_id}...",
      "footer": "Kiitos ostoksesta!"
    },
    "minimal": {
      "name": "Minimaalinen / Minimal",
      "logo": "*** {name} ***",
      "header_format": "{name} | {business_id}",
      "footer": "Kiitos!"
    }
  },
  "history": []
}
```

### Template System

Templates control how receipts are formatted:
- **logo**: ASCII art logo (supports {name}, {business_id}, etc.)
- **header_format**: Company info layout
- **footer**: Closing message

Select templates in GUI via radio buttons or programmatically via API.

## 🖥️ Terminal Editor

When using terminal mode (`--edit` or `--edit-logo`), the tool uses:
1. `$EDITOR` environment variable (if set)
2. Falls back to `nano` if not set

The editor opens a temporary file with:
- Instructions at the top (lines starting with #)
- Current content below
- Save and close to apply changes

## 📦 Classes and API

### `Product`
```python
product = Product("Kaivinkone", 1, 850.0)
total = product.total()  # 850.0
data = product.to_dict()
```

### `Receipt`
```python
receipt = Receipt()
receipt.add_product("Item", 2, 100.0)
receipt.current_template = "minimal"

# Generate text
text = receipt.generate_text()

# Manual override
receipt.set_manual_override("Custom receipt text")

# Get/set logo
logo = receipt.get_logo()
receipt.set_logo("New ASCII logo")

# Save to history
receipt.save_to_history()

# Export
receipt_data = receipt.to_dict()
```

### `ReceiptExporter`
```python
# Export to TXT
ReceiptExporter.export_txt(receipt, "receipt.txt")

# Export to PDF (requires reportlab)
ReceiptExporter.export_pdf(receipt, "receipt.pdf")
```

### `ReceiptEditor`
```python
# Edit in terminal
ReceiptEditor.edit_logo(receipt)
ReceiptEditor.edit_receipt(receipt)
```

## 🧪 Testing

Run the test suite:

```bash
python3 test_receipt_tool.py
```

Run smoke test:

```bash
python3 receipt_tool.py --smoke-test
```

Test coverage:
- Product class (creation, calculations, serialization)
- Receipt class (products, calculations, text generation, templates)
- Logo validation and cleanup
- Manual override functionality
- Export to TXT and PDF
- Configuration management
- CLI operations

## 🎯 Use Cases

### 1. Quick Receipt Generation
```bash
# Start GUI, add products, export
python3 receipt_tool.py
```

### 2. Batch Processing
```bash
# Create receipts programmatically
python3 -c "
from receipt_tool import Receipt, ReceiptExporter
r = Receipt()
r.add_product('Item', 1, 100.0)
ReceiptExporter.export_txt(r, 'batch_receipt.txt')
"
```

### 3. Custom Templates
Edit `receipt_tool.json` to add custom templates:
```json
{
  "templates": {
    "invoice": {
      "name": "Invoice / Lasku",
      "logo": "INVOICE\n{name}",
      "header_format": "INVOICE #{invoice_no}\n{name}",
      "footer": "Payment due in 30 days"
    }
  }
}
```

### 4. Logo Branding
```bash
# Edit logo in terminal
python3 receipt_tool.py --edit-logo

# Or edit directly in config file
nano receipt_tool.json
```

## 📋 Requirements

- **Python**: 3.8+ (3.10+ recommended)
- **Required**: Standard library only
- **Optional**:
  - `tkinter` - GUI support (usually pre-installed)
  - `reportlab` - PDF export
  - `pillow` - Advanced image handling

## 🔒 Security

### Control Character Cleanup
All text input is sanitized to remove control characters (\x00-\x1f) except:
- `\n` (newline) - allowed for formatting
- `\t` (tab) - allowed for alignment

### Logo Validation
- Maximum line width checked against configured width
- Prevents overly wide logos that break formatting

### Safe Defaults
- Config file uses safe JSON serialization
- Temp files cleaned up after editor use
- No code execution in templates (format strings only)

## 🤝 Contributing

This is a single-file implementation for easy maintenance. When contributing:
1. Keep all code in `receipt_tool.py`
2. Add tests to `test_receipt_tool.py`
3. Run smoke test before committing
4. Update this README for new features

## 📄 License

Part of Harjun Raskaskone Oy (HRK) project.
See main project README for license information.

## 🐛 Troubleshooting

### GUI Not Available
```bash
# Install tkinter
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install python3-tkinter  # CentOS/RHEL
brew install python-tk            # macOS
```

### PDF Export Fails
```bash
# Install reportlab
pip install reportlab
```

### Terminal Editor Not Working
```bash
# Set EDITOR environment variable
export EDITOR=vim
# or
export EDITOR=nano
# or
export EDITOR=code  # VS Code
```

### Config File Issues
```bash
# Delete and regenerate
rm receipt_tool.json
python3 receipt_tool.py --smoke-test
```

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/AnomFIN/hrk
- Email: info@hrk.fi

---

Made with ❤️ for Harjun Raskaskone Oy (HRK)
