#!/usr/bin/env python3
"""
Receipt Tool - Advanced Receipt Editor with ASCII Logo Support
Harjun Raskaskone Oy (HRK)

Full-featured receipt editor with:
- ASCII logo editing (GUI & terminal)
- Full receipt text editing
- Real-time preview
- Template management
- Receipt history
- Export to TXT and PDF
"""

import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Try to import GUI libraries
GUI_AVAILABLE = False
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    pass

# Try to import reportlab for PDF export
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass

# Constants
CONFIG_FILE = "receipt_tool.json"
DEFAULT_WIDTH = 50
DEFAULT_VAT_RATE = 0.24

DEFAULT_LOGO = """
╔═══════════════════════════════════════╗
║   HARJUN RASKASKONE OY (HRK)          ║
║   Laadukasta laitevuokrausta          ║
╚═══════════════════════════════════════╝
"""

DEFAULT_CONFIG = {
    "logo_ascii": DEFAULT_LOGO.strip(),
    "width": DEFAULT_WIDTH,
    "vat_rate": DEFAULT_VAT_RATE,
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
            "logo": DEFAULT_LOGO.strip(),
            "header_format": "{name}\nY-tunnus: {business_id}\n{address}\nPuh: {phone}",
            "footer": "Kiitos ostoksesta! / Thank you for your purchase!"
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


class Product:
    """Product object"""
    def __init__(self, name: str, quantity: int, price: float):
        self.name = name
        self.quantity = quantity
        self.price = price
    
    def total(self) -> float:
        return self.quantity * self.price
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(data["name"], data["quantity"], data["price"])


class Receipt:
    """Enhanced Receipt class with template and manual override support"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._load_config()
        self.products: List[Product] = []
        self._manual_override_text: Optional[str] = None
        self.current_template = "default"
        
        # Load from config
        self.company_info = self.config.get("company_info", DEFAULT_CONFIG["company_info"])
        self.vat_rate = self.config.get("vat_rate", DEFAULT_VAT_RATE)
        self.width = self.config.get("width", DEFAULT_WIDTH)
    
    @staticmethod
    def _load_config() -> Dict:
        """Load configuration from JSON file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        return DEFAULT_CONFIG.copy()
    
    @staticmethod
    def _save_config(config: Dict) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_logo(self) -> str:
        """Get current logo from config or template"""
        template = self.config.get("templates", {}).get(self.current_template, {})
        if template:
            logo = template.get("logo", "")
            # Format logo with company info
            return logo.format(**self.company_info)
        return self.config.get("logo_ascii", DEFAULT_LOGO).strip()
    
    def set_logo(self, logo: str) -> bool:
        """Set and save logo to config"""
        # Clean and validate
        logo = self._cleanup_text(logo)
        if not self._validate_logo(logo):
            return False
        
        self.config["logo_ascii"] = logo
        return self._save_config(self.config)
    
    def _cleanup_text(self, text: str) -> str:
        """Remove control characters except \n and \t"""
        # Remove control characters (\x00-\x1f) except \n (0x0a) and \t (0x09)
        cleaned = ""
        for char in text:
            code = ord(char)
            if code >= 0x20 or char in ['\n', '\t']:
                cleaned += char
        return cleaned
    
    def _validate_logo(self, logo: str) -> bool:
        """Validate logo max line width"""
        lines = logo.split('\n')
        max_line_width = max(len(line) for line in lines) if lines else 0
        if max_line_width > self.width + 10:  # Allow some overflow
            print(f"Warning: Logo line width {max_line_width} exceeds configured width {self.width}")
            return False
        return True
    
    def add_product(self, name: str, quantity: int, price: float) -> bool:
        """Add product"""
        try:
            if quantity <= 0 or price < 0:
                return False
            self.products.append(Product(name, quantity, price))
            return True
        except Exception:
            return False
    
    def remove_product(self, index: int) -> bool:
        """Remove product"""
        try:
            if 0 <= index < len(self.products):
                self.products.pop(index)
                return True
            return False
        except Exception:
            return False
    
    def get_subtotal(self) -> float:
        return sum(p.total() for p in self.products)
    
    def get_vat(self) -> float:
        return self.get_subtotal() * self.vat_rate
    
    def get_total(self) -> float:
        return self.get_subtotal() + self.get_vat()
    
    def generate_text(self) -> str:
        """Generate text receipt (uses override if set)"""
        if self._manual_override_text:
            return self._cleanup_text(self._manual_override_text)
        
        lines = []
        
        # Logo
        logo = self.get_logo()
        if logo:
            lines.append(logo)
        
        # Header
        template = self.config.get("templates", {}).get(self.current_template, {})
        header_format = template.get("header_format", "")
        if header_format:
            lines.append("")
            lines.append(header_format.format(**self.company_info))
        else:
            lines.append(f"\n{self.company_info['name']}")
            lines.append(f"Y-tunnus: {self.company_info['business_id']}")
            lines.append(f"{self.company_info['address']}")
            lines.append(f"Puh: {self.company_info['phone']}")
        
        # Date
        lines.append(f"\nPäivämäärä: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        lines.append("\n" + "=" * self.width)
        
        # Products
        lines.append("\nTUOTTEET / PRODUCTS:")
        lines.append("-" * self.width)
        
        for i, product in enumerate(self.products, 1):
            lines.append(f"{i}. {product.name}")
            lines.append(f"   {product.quantity} kpl x {product.price:.2f} € = {product.total():.2f} €")
        
        # Totals
        lines.append("-" * self.width)
        lines.append(f"Välisumma (ilman ALV): {self.get_subtotal():.2f} €")
        lines.append(f"ALV {int(self.vat_rate * 100)}%: {self.get_vat():.2f} €")
        lines.append("=" * self.width)
        lines.append(f"YHTEENSÄ: {self.get_total():.2f} €")
        lines.append("=" * self.width)
        
        # Footer
        footer = template.get("footer", "Kiitos ostoksesta! / Thank you for your purchase!")
        lines.append(f"\n{footer}")
        lines.append("")
        
        return "\n".join(lines)
    
    def set_manual_override(self, text: Optional[str]):
        """Set manual override text"""
        if text:
            self._manual_override_text = self._cleanup_text(text)
        else:
            self._manual_override_text = None
    
    def save_to_history(self):
        """Save current receipt to history"""
        history_item = {
            "timestamp": datetime.now().isoformat(),
            "products": [p.to_dict() for p in self.products],
            "template": self.current_template,
            "total": self.get_total(),
            "text_preview": self.generate_text()[:200]  # First 200 chars
        }
        
        if "history" not in self.config:
            self.config["history"] = []
        
        self.config["history"].insert(0, history_item)
        # Keep only last 50 receipts
        self.config["history"] = self.config["history"][:50]
        self._save_config(self.config)
    
    def to_dict(self) -> Dict:
        """Export receipt to dictionary"""
        return {
            "products": [p.to_dict() for p in self.products],
            "template": self.current_template,
            "company_info": self.company_info,
            "totals": {
                "subtotal": self.get_subtotal(),
                "vat": self.get_vat(),
                "total": self.get_total()
            }
        }


class ReceiptExporter:
    """Export receipts to various formats"""
    
    @staticmethod
    def export_txt(receipt: Receipt, filepath: str) -> bool:
        """Export receipt as TXT"""
        try:
            text = receipt.generate_text()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            print(f"Error exporting TXT: {e}")
            return False
    
    @staticmethod
    def export_pdf(receipt: Receipt, filepath: str) -> bool:
        """Export receipt as PDF"""
        if not REPORTLAB_AVAILABLE:
            print("Error: reportlab library is required for PDF export")
            print("Install with: pip install reportlab")
            return False
        
        try:
            text = receipt.generate_text()
            lines = text.split('\n')
            
            # Create PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # Use monospace font
            font_name = "Courier"
            font_size = 10
            line_height = font_size + 2
            
            # Starting position
            x = 30
            y = height - 50
            
            c.setFont(font_name, font_size)
            
            for line in lines:
                if y < 50:  # Start new page if needed
                    c.showPage()
                    c.setFont(font_name, font_size)
                    y = height - 50
                
                c.drawString(x, y, line)
                y -= line_height
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return False


class ReceiptEditor:
    """Terminal-based receipt editor using $EDITOR"""
    
    @staticmethod
    def edit_text(initial_text: str, title: str = "Edit Text") -> Optional[str]:
        """Edit text using system editor"""
        editor = os.environ.get('EDITOR', 'nano')
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(f"# {title}\n")
            f.write("# Save and close to apply changes\n")
            f.write("# Lines starting with # will be removed\n\n")
            f.write(initial_text)
            temp_path = f.name
        
        try:
            # Open editor
            subprocess.call([editor, temp_path])
            
            # Read result
            with open(temp_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Remove comment lines
            result = ''.join(line for line in lines if not line.startswith('#'))
            return result.strip()
            
        except Exception as e:
            print(f"Error editing text: {e}")
            return None
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass
    
    @staticmethod
    def edit_logo(receipt: Receipt) -> bool:
        """Edit logo in terminal"""
        current_logo = receipt.get_logo()
        new_logo = ReceiptEditor.edit_text(current_logo, "Edit ASCII Logo")
        
        if new_logo is not None and new_logo != current_logo:
            if receipt.set_logo(new_logo):
                print("✓ Logo updated successfully")
                return True
            else:
                print("✗ Failed to update logo")
                return False
        return False
    
    @staticmethod
    def edit_receipt(receipt: Receipt) -> bool:
        """Edit full receipt text"""
        current_text = receipt.generate_text()
        new_text = ReceiptEditor.edit_text(current_text, "Edit Full Receipt")
        
        if new_text is not None and new_text != current_text:
            receipt.set_manual_override(new_text)
            print("✓ Receipt text updated successfully")
            return True
        return False


class ReceiptToolGUI:
    """Beautiful GUI for receipt tool"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Receipt Tool - HRK")
        self.root.geometry("1000x700")
        
        # Configure colors
        self.bg_primary = "#2c3e50"
        self.bg_secondary = "#34495e"
        self.bg_light = "#ecf0f1"
        self.accent_blue = "#3498db"
        self.accent_green = "#27ae60"
        self.accent_purple = "#9b59b6"
        self.accent_red = "#e74c3c"
        
        self.receipt = Receipt()
        
        self.create_ui()
        self.update_preview()
    
    def create_ui(self):
        """Create beautiful UI"""
        # Top bar
        top_bar = tk.Frame(self.root, bg=self.bg_primary, height=60)
        top_bar.pack(fill=tk.X)
        
        title = tk.Label(
            top_bar,
            text="🧾 RECEIPT TOOL - KUITTITYÖKALU",
            font=("Arial", 18, "bold"),
            bg=self.bg_primary,
            fg="white"
        )
        title.pack(pady=15)
        
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg=self.bg_light, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Template selector
        template_frame = tk.LabelFrame(left_panel, text="📋 Template / Pohja", bg=self.bg_light, font=("Arial", 10, "bold"))
        template_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.template_var = tk.StringVar(value=self.receipt.current_template)
        templates = self.receipt.config.get("templates", {})
        
        for template_id, template_data in templates.items():
            rb = tk.Radiobutton(
                template_frame,
                text=template_data.get("name", template_id),
                variable=self.template_var,
                value=template_id,
                bg=self.bg_light,
                command=self.on_template_change
            )
            rb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Product entry
        product_frame = tk.LabelFrame(left_panel, text="➕ Add Product / Lisää Tuote", bg=self.bg_light, font=("Arial", 10, "bold"))
        product_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(product_frame, text="Name:", bg=self.bg_light).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.name_entry = tk.Entry(product_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=3)
        
        tk.Label(product_frame, text="Qty:", bg=self.bg_light).grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.qty_entry = tk.Entry(product_frame, width=10)
        self.qty_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        tk.Label(product_frame, text="Price €:", bg=self.bg_light).grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.price_entry = tk.Entry(product_frame, width=10)
        self.price_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)
        
        btn_add = tk.Button(
            product_frame,
            text="Add / Lisää",
            command=self.add_product,
            bg=self.accent_green,
            fg="white",
            font=("Arial", 9, "bold")
        )
        btn_add.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Products list
        list_frame = tk.LabelFrame(left_panel, text="🛒 Products / Tuotteet", bg=self.bg_light, font=("Arial", 10, "bold"))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.products_listbox = tk.Listbox(list_frame, height=8)
        self.products_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        btn_remove = tk.Button(
            list_frame,
            text="Remove Selected / Poista",
            command=self.remove_product,
            bg=self.accent_red,
            fg="white"
        )
        btn_remove.pack(pady=5)
        
        # Action buttons
        actions_frame = tk.LabelFrame(left_panel, text="⚡ Actions / Toiminnot", bg=self.bg_light, font=("Arial", 10, "bold"))
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        buttons = [
            ("🎨 Edit Logo", self.edit_logo, self.accent_blue),
            ("✏️ Edit Receipt", self.edit_receipt, self.accent_purple),
            ("💾 Save TXT", self.save_txt, self.accent_green),
            ("📄 Export PDF", self.export_pdf, self.accent_red),
            ("📜 History", self.show_history, self.bg_secondary),
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                width=20
            )
            btn.pack(pady=3)
        
        # Right panel - Preview
        right_panel = tk.Frame(main_container, bg=self.bg_light)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        preview_label = tk.Label(
            right_panel,
            text="👁️ PREVIEW / ESIKATSELU",
            bg=self.bg_secondary,
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        )
        preview_label.pack(fill=tk.X)
        
        # Preview text area
        self.preview_text = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.NONE,
            font=("Courier New", 9),
            bg="white",
            fg="black",
            width=60,
            height=35
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def on_template_change(self):
        """Handle template change"""
        self.receipt.current_template = self.template_var.get()
        self.update_preview()
    
    def add_product(self):
        """Add product"""
        try:
            name = self.name_entry.get().strip()
            qty = int(self.qty_entry.get().strip())
            price = float(self.price_entry.get().strip())
            
            if not name:
                messagebox.showwarning("Invalid Input", "Product name is required")
                return
            
            if self.receipt.add_product(name, qty, price):
                self.name_entry.delete(0, tk.END)
                self.qty_entry.delete(0, tk.END)
                self.price_entry.delete(0, tk.END)
                self.update_products_list()
                self.update_preview()
            else:
                messagebox.showerror("Error", "Invalid product values")
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price")
    
    def remove_product(self):
        """Remove selected product"""
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a product to remove")
            return
        
        index = selection[0]
        if self.receipt.remove_product(index):
            self.update_products_list()
            self.update_preview()
    
    def update_products_list(self):
        """Update products listbox"""
        self.products_listbox.delete(0, tk.END)
        for i, product in enumerate(self.receipt.products):
            text = f"{i+1}. {product.name} - {product.quantity}x {product.price:.2f}€ = {product.total():.2f}€"
            self.products_listbox.insert(tk.END, text)
    
    def update_preview(self):
        """Update preview panel"""
        self.preview_text.delete(1.0, tk.END)
        preview = self.receipt.generate_text()
        self.preview_text.insert(1.0, preview)
    
    def edit_logo(self):
        """Edit logo in GUI dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit ASCII Logo")
        dialog.geometry("600x500")
        
        tk.Label(dialog, text="Edit ASCII Logo", font=("Arial", 12, "bold")).pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(
            dialog,
            wrap=tk.NONE,
            font=("Courier New", 10),
            width=60,
            height=20
        )
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_area.insert(1.0, self.receipt.get_logo())
        
        def save():
            new_logo = text_area.get(1.0, tk.END).strip()
            if self.receipt.set_logo(new_logo):
                messagebox.showinfo("Success", "Logo updated successfully!")
                self.update_preview()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Logo validation failed - line too wide")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Save", command=save, bg=self.accent_green, fg="white", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg=self.accent_red, fg="white", width=10).pack(side=tk.LEFT, padx=5)
    
    def edit_receipt(self):
        """Edit full receipt text in GUI dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Full Receipt")
        dialog.geometry("700x600")
        
        tk.Label(dialog, text="Edit Full Receipt Text", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(dialog, text="Note: This will override the generated receipt text", fg="red").pack()
        
        text_area = scrolledtext.ScrolledText(
            dialog,
            wrap=tk.NONE,
            font=("Courier New", 9),
            width=70,
            height=30
        )
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_area.insert(1.0, self.receipt.generate_text())
        
        def save():
            new_text = text_area.get(1.0, tk.END).strip()
            self.receipt.set_manual_override(new_text)
            messagebox.showinfo("Success", "Receipt text updated!")
            self.update_preview()
            dialog.destroy()
        
        def clear_override():
            self.receipt.set_manual_override(None)
            messagebox.showinfo("Success", "Manual override cleared! Using generated text.")
            self.update_preview()
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Save", command=save, bg=self.accent_green, fg="white", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Override", command=clear_override, bg=self.accent_purple, fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg=self.accent_red, fg="white", width=10).pack(side=tk.LEFT, padx=5)
    
    def save_txt(self):
        """Save receipt as TXT"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filepath:
            if ReceiptExporter.export_txt(self.receipt, filepath):
                self.receipt.save_to_history()
                messagebox.showinfo("Success", f"Receipt saved to:\n{filepath}")
            else:
                messagebox.showerror("Error", "Failed to save receipt")
    
    def export_pdf(self):
        """Export receipt as PDF"""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "reportlab library is required for PDF export.\n\n"
                "Install with:\npip install reportlab"
            )
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if filepath:
            if ReceiptExporter.export_pdf(self.receipt, filepath):
                self.receipt.save_to_history()
                messagebox.showinfo("Success", f"Receipt exported to:\n{filepath}")
            else:
                messagebox.showerror("Error", "Failed to export PDF")
    
    def show_history(self):
        """Show receipt history"""
        history = self.receipt.config.get("history", [])
        
        if not history:
            messagebox.showinfo("History", "No receipts in history")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Receipt History")
        dialog.geometry("800x500")
        
        tk.Label(dialog, text="📜 Receipt History", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create treeview
        tree_frame = tk.Frame(dialog)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Date", "Template", "Total", "Preview")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("Date", text="Date")
        tree.heading("Template", text="Template")
        tree.heading("Total", text="Total (€)")
        tree.heading("Preview", text="Preview")
        
        tree.column("Date", width=150)
        tree.column("Template", width=100)
        tree.column("Total", width=100)
        tree.column("Preview", width=400)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate history
        for item in history:
            timestamp = datetime.fromisoformat(item["timestamp"]).strftime("%Y-%m-%d %H:%M")
            template = item.get("template", "default")
            total = f"{item.get('total', 0):.2f}"
            preview = item.get("text_preview", "")[:80] + "..."
            
            tree.insert("", tk.END, values=(timestamp, template, total, preview))
        
        tk.Button(dialog, text="Close", command=dialog.destroy, bg=self.accent_blue, fg="white").pack(pady=10)


class ReceiptToolCLI:
    """Command-line interface for receipt tool"""
    
    def __init__(self):
        self.receipt = Receipt()
    
    def preview(self):
        """Show preview in console"""
        print("\n" + "=" * 60)
        print("PREVIEW / ESIKATSELU")
        print("=" * 60)
        print(self.receipt.generate_text())
        print("=" * 60 + "\n")
    
    def edit_logo(self):
        """Edit logo in terminal"""
        if ReceiptEditor.edit_logo(self.receipt):
            print("\n✓ Logo updated")
            self.preview()
        else:
            print("\n✗ Logo not changed")
    
    def edit_receipt(self):
        """Edit full receipt"""
        if ReceiptEditor.edit_receipt(self.receipt):
            print("\n✓ Receipt updated")
            self.preview()
        else:
            print("\n✗ Receipt not changed")
    
    def save_txt(self, path: str):
        """Save as TXT"""
        if ReceiptExporter.export_txt(self.receipt, path):
            self.receipt.save_to_history()
            print(f"✓ Receipt saved to: {path}")
        else:
            print(f"✗ Failed to save receipt")
    
    def export_pdf(self, path: str):
        """Export as PDF"""
        if not REPORTLAB_AVAILABLE:
            print("✗ Error: reportlab library is required for PDF export")
            print("  Install with: pip install reportlab")
            return
        
        if ReceiptExporter.export_pdf(self.receipt, path):
            self.receipt.save_to_history()
            print(f"✓ Receipt exported to: {path}")
        else:
            print(f"✗ Failed to export PDF")
    
    @staticmethod
    def smoke_test():
        """Run smoke test"""
        print("\n" + "=" * 60)
        print("SMOKE TEST - Receipt Tool")
        print("=" * 60 + "\n")
        
        # Create demo receipt
        print("1. Creating demo receipt...")
        receipt = Receipt()
        receipt.add_product("Kaivinkone 15t", 1, 850.00)
        receipt.add_product("Kuorma-auto", 2, 450.00)
        receipt.add_product("Nosturi", 1, 1200.00)
        print("   ✓ Demo products added")
        
        # Test TXT export
        print("\n2. Testing TXT export...")
        txt_path = f"/tmp/smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        if ReceiptExporter.export_txt(receipt, txt_path):
            print(f"   ✓ TXT exported to: {txt_path}")
            print(f"   File size: {os.path.getsize(txt_path)} bytes")
        else:
            print("   ✗ TXT export failed")
            return 1
        
        # Test PDF export
        print("\n3. Testing PDF export...")
        if REPORTLAB_AVAILABLE:
            pdf_path = f"/tmp/smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            if ReceiptExporter.export_pdf(receipt, pdf_path):
                print(f"   ✓ PDF exported to: {pdf_path}")
                print(f"   File size: {os.path.getsize(pdf_path)} bytes")
            else:
                print("   ✗ PDF export failed")
                return 1
        else:
            print("   ⚠ reportlab not available - PDF export skipped")
            print("     Install with: pip install reportlab")
        
        # Test config
        print("\n4. Testing configuration...")
        if os.path.exists(CONFIG_FILE):
            print(f"   ✓ Config file exists: {CONFIG_FILE}")
        else:
            print(f"   ⚠ Config file will be created on first save")
        
        # Summary
        print("\n" + "=" * 60)
        print("SMOKE TEST COMPLETED SUCCESSFULLY ✓")
        print("=" * 60)
        print(f"\nDemo files created:")
        print(f"  - {txt_path}")
        if REPORTLAB_AVAILABLE:
            print(f"  - {pdf_path}")
        print("\n")
        
        return 0


def print_help():
    """Print help message"""
    help_text = """
╔═══════════════════════════════════════════════════════════════╗
║           RECEIPT TOOL - KUITTITYÖKALU                        ║
║           Harjun Raskaskone Oy (HRK)                          ║
╚═══════════════════════════════════════════════════════════════╝

Usage: receipt_tool.py [OPTIONS]

OPTIONS:
  --gui              Launch GUI application (default if available)
  --terminal         Force terminal mode
  --edit             Edit full receipt in terminal editor
  --edit-logo        Edit ASCII logo in terminal editor
  --preview          Show receipt preview in console
  --save-txt PATH    Save receipt as TXT file
  --export-pdf PATH  Export receipt as PDF file
  --smoke-test       Run smoke test with demo receipt
  --help             Show this help message

EXAMPLES:
  # Launch GUI
  python receipt_tool.py
  
  # Edit logo in terminal
  python receipt_tool.py --edit-logo
  
  # Preview and save
  python receipt_tool.py --preview --save-txt receipt.txt
  
  # Export to PDF
  python receipt_tool.py --export-pdf receipt.pdf
  
  # Run smoke test
  python receipt_tool.py --smoke-test

CONFIGURATION:
  Config file: receipt_tool.json
  - logo_ascii: ASCII logo
  - width: Receipt width (default: 50)
  - vat_rate: VAT rate (default: 0.24)
  - company_info: Company details
  - templates: Receipt templates
  - history: Receipt history (last 50)

DEPENDENCIES:
  Required:  Python 3.8+
  Optional:  tkinter (GUI), reportlab (PDF export)

EDITOR:
  Terminal editing uses $EDITOR environment variable
  Default: nano

For more information, visit: https://github.com/AnomFIN/hrk
"""
    print(help_text)


def main():
    """Main entry point"""
    args = sys.argv[1:]
    
    # Help
    if "--help" in args or "-h" in args:
        print_help()
        return 0
    
    # Smoke test
    if "--smoke-test" in args:
        return ReceiptToolCLI.smoke_test()
    
    # CLI mode with flags
    if any(flag in args for flag in ["--edit", "--edit-logo", "--preview", "--save-txt", "--export-pdf"]):
        cli = ReceiptToolCLI()
        
        if "--edit-logo" in args:
            cli.edit_logo()
        
        if "--edit" in args:
            cli.edit_receipt()
        
        if "--preview" in args:
            cli.preview()
        
        if "--save-txt" in args:
            idx = args.index("--save-txt")
            if idx + 1 < len(args):
                cli.save_txt(args[idx + 1])
            else:
                print("Error: --save-txt requires a file path")
                return 1
        
        if "--export-pdf" in args:
            idx = args.index("--export-pdf")
            if idx + 1 < len(args):
                cli.export_pdf(args[idx + 1])
            else:
                print("Error: --export-pdf requires a file path")
                return 1
        
        return 0
    
    # GUI mode (default)
    if GUI_AVAILABLE and "--terminal" not in args:
        root = tk.Tk()
        app = ReceiptToolGUI(root)
        root.mainloop()
        return 0
    else:
        if not GUI_AVAILABLE:
            print("Tkinter not available. Use CLI flags for terminal mode.")
            print("Run with --help for usage information.")
        else:
            print("Terminal mode requested but no CLI flags provided.")
            print("Run with --help for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
