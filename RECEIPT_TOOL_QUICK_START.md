# Receipt Tool - Quick Start Guide

## 🚀 5-Minute Quick Start

### Installation
```bash
# No installation needed! Just run:
python3 receipt_tool.py --help
```

### First Receipt - GUI Method (Easiest)
```bash
# Launch GUI
python3 receipt_tool.py

# In GUI:
# 1. Select template (Default or Minimal)
# 2. Add products:
#    - Name: "Kaivinkone 15t"
#    - Quantity: 1
#    - Price: 850
#    - Click "Add"
# 3. See preview update in real-time
# 4. Click "💾 Save TXT" to export
```

### First Receipt - CLI Method (Fast)
```bash
# Preview empty receipt
python3 receipt_tool.py --preview

# Create and save receipt programmatically
python3 -c "
from receipt_tool import Receipt, ReceiptExporter
r = Receipt()
r.add_product('Kaivinkone', 1, 850.00)
ReceiptExporter.export_txt(r, 'my_receipt.txt')
print('Receipt saved!')
"
```

## 📋 Common Tasks

### Edit ASCII Logo
```bash
# GUI method
python3 receipt_tool.py
# Click "🎨 Edit Logo" button

# Terminal method
python3 receipt_tool.py --edit-logo
# Your $EDITOR opens, edit and save
```

### Create Custom Receipt
```bash
# GUI method
python3 receipt_tool.py
# Click "✏️ Edit Receipt" button
# Edit full text, save

# Terminal method
python3 receipt_tool.py --edit
```

### Switch Templates
```python
from receipt_tool import Receipt
r = Receipt()
r.current_template = "minimal"  # or "default"
```

### Export to PDF
```bash
# Install reportlab first
pip install reportlab

# Then export
python3 receipt_tool.py --export-pdf receipt.pdf
```

### View History
```bash
# In GUI
python3 receipt_tool.py
# Click "📜 History" button

# Programmatically
python3 -c "
import json
with open('receipt_tool.json') as f:
    config = json.load(f)
    for item in config['history']:
        print(item['timestamp'], item['total'])
"
```

## 🎨 Customization

### Add New Template
Edit `receipt_tool.json`:
```json
{
  "templates": {
    "invoice": {
      "name": "Invoice",
      "logo": "INVOICE\n{name}",
      "header_format": "{name}\nInvoice #{invoice_no}",
      "footer": "Payment due in 30 days"
    }
  }
}
```

### Change Company Info
Edit `receipt_tool.json`:
```json
{
  "company_info": {
    "name": "Your Company",
    "business_id": "123456-7",
    "address": "Your Address",
    "phone": "+358 XX XXXXXXX"
  }
}
```

### Change Receipt Width
Edit `receipt_tool.json`:
```json
{
  "width": 60
}
```

## 🧪 Testing

### Run Tests
```bash
python3 test_receipt_tool.py
```

### Run Smoke Test
```bash
python3 receipt_tool.py --smoke-test
```

### Run Demo
```bash
python3 demo_receipt_tool.py
```

## 🆘 Troubleshooting

### GUI doesn't open
```bash
# Install tkinter
sudo apt-get install python3-tk  # Ubuntu/Debian
```

### PDF export fails
```bash
# Install reportlab
pip install reportlab
```

### Editor doesn't open
```bash
# Set EDITOR variable
export EDITOR=nano  # or vim, code, etc.
```

### Config file corrupted
```bash
# Delete and regenerate
rm receipt_tool.json
python3 receipt_tool.py --smoke-test
```

## 📖 More Information

- Full documentation: `RECEIPT_TOOL_README.md`
- Run demo: `python3 demo_receipt_tool.py`
- Get help: `python3 receipt_tool.py --help`

## 💡 Pro Tips

1. **Use templates** for different receipt styles
2. **Save to history** to track all receipts
3. **Custom logos** make receipts unique
4. **Manual override** for special cases
5. **Smoke test** validates everything works

## ⚡ One-Liners

```bash
# Quick preview
python3 receipt_tool.py --preview

# Edit and save
python3 receipt_tool.py --edit --save-txt output.txt

# Test everything
python3 receipt_tool.py --smoke-test

# Beautiful GUI
python3 receipt_tool.py

# Help
python3 receipt_tool.py --help
```

---

**Made with ❤️ for Harjun Raskaskone Oy (HRK)**
