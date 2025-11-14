#!/usr/bin/env python3
"""
GUI demonstration script - adds sample data and takes screenshot
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import tkinter as tk
    from receipt_app import ReceiptAppGUI, Receipt
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def main():
    """Create GUI with sample data"""
    root = tk.Tk()
    app = ReceiptAppGUI(root)
    
    # Add sample products programmatically
    app.receipt.add_product("Kaivinkone 15t", 2, 850.00)
    app.receipt.add_product("Kuorma-auto", 3, 450.00)
    app.receipt.add_product("Nosturi 25t", 1, 1200.00)
    
    # Update display
    app.update_display()
    
    # Keep window open for a moment
    root.after(3000, root.quit)  # Close after 3 seconds
    
    print("GUI demo running...")
    root.mainloop()
    print("GUI demo completed")


if __name__ == "__main__":
    main()
