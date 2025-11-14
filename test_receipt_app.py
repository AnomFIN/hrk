#!/usr/bin/env python3
"""Test suite for receipt_app.py"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

import receipt_app


class TestProduct(unittest.TestCase):
    """Test Product class"""
    
    def test_product_creation(self):
        """Test creating a product"""
        product = receipt_app.Product("Test Item", 2, 10.0)
        self.assertEqual(product.name, "Test Item")
        self.assertEqual(product.quantity, 2)
        self.assertEqual(product.price, 10.0)
    
    def test_product_total(self):
        """Test product total calculation"""
        product = receipt_app.Product("Test Item", 3, 15.5)
        self.assertEqual(product.total(), 46.5)
    
    def test_product_to_dict(self):
        """Test product to dictionary conversion"""
        product = receipt_app.Product("Test Item", 2, 10.0)
        data = product.to_dict()
        self.assertEqual(data["name"], "Test Item")
        self.assertEqual(data["quantity"], 2)
        self.assertEqual(data["price"], 10.0)


class TestReceipt(unittest.TestCase):
    """Test Receipt class"""
    
    def setUp(self):
        """Set up test receipt"""
        self.receipt = receipt_app.Receipt()
    
    def test_empty_receipt(self):
        """Test empty receipt calculations"""
        self.assertEqual(len(self.receipt.products), 0)
        self.assertEqual(self.receipt.get_subtotal(), 0.0)
        self.assertEqual(self.receipt.get_vat(), 0.0)
        self.assertEqual(self.receipt.get_total(), 0.0)
    
    def test_add_product(self):
        """Test adding a product"""
        result = self.receipt.add_product("Kaivinkone", 1, 850.0)
        self.assertTrue(result)
        self.assertEqual(len(self.receipt.products), 1)
        self.assertEqual(self.receipt.products[0].name, "Kaivinkone")
    
    def test_add_invalid_product(self):
        """Test adding invalid products"""
        # Negative quantity
        result = self.receipt.add_product("Item", -1, 10.0)
        self.assertFalse(result)
        
        # Zero quantity
        result = self.receipt.add_product("Item", 0, 10.0)
        self.assertFalse(result)
        
        # Negative price
        result = self.receipt.add_product("Item", 1, -10.0)
        self.assertFalse(result)
    
    def test_remove_product(self):
        """Test removing a product"""
        self.receipt.add_product("Item 1", 1, 10.0)
        self.receipt.add_product("Item 2", 2, 20.0)
        
        result = self.receipt.remove_product(0)
        self.assertTrue(result)
        self.assertEqual(len(self.receipt.products), 1)
        self.assertEqual(self.receipt.products[0].name, "Item 2")
    
    def test_remove_invalid_index(self):
        """Test removing with invalid index"""
        self.receipt.add_product("Item", 1, 10.0)
        
        # Index out of range
        result = self.receipt.remove_product(5)
        self.assertFalse(result)
        
        # Negative index should be rejected
        result = self.receipt.remove_product(-1)
        self.assertFalse(result)
    
    def test_calculations(self):
        """Test receipt calculations"""
        self.receipt.add_product("Item 1", 2, 100.0)  # 200.0
        self.receipt.add_product("Item 2", 1, 50.0)   # 50.0
        
        subtotal = self.receipt.get_subtotal()
        self.assertEqual(subtotal, 250.0)
        
        vat = self.receipt.get_vat()
        self.assertEqual(vat, 60.0)  # 24% of 250
        
        total = self.receipt.get_total()
        self.assertEqual(total, 310.0)
    
    def test_generate_text(self):
        """Test text receipt generation"""
        self.receipt.add_product("Kaivinkone 15t", 1, 850.0)
        text = self.receipt.generate_text()
        
        # Check for key elements
        self.assertIn("HARJUN RASKASKONE OY", text)
        self.assertIn("Kaivinkone 15t", text)
        self.assertIn("850.00", text)
        self.assertIn("ALV 24%", text)
        self.assertIn("YHTEENSÄ", text)


class TestReceiptPrinter(unittest.TestCase):
    """Test ReceiptPrinter class"""
    
    def test_save_as_png(self):
        """Test saving receipt as PNG"""
        if not receipt_app.PILLOW_AVAILABLE:
            self.skipTest("Pillow not available")
        
        receipt = receipt_app.Receipt()
        receipt.add_product("Test Product", 1, 10.0)
        text = receipt.generate_text()
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_path = f.name
        
        try:
            result = receipt_app.ReceiptPrinter.save_as_png(text, temp_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            
            # Check file size is reasonable
            size = os.path.getsize(temp_path)
            self.assertGreater(size, 100)  # At least 100 bytes
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestTerminalApp(unittest.TestCase):
    """Test Terminal Application"""
    
    def test_terminal_app_creation(self):
        """Test creating terminal app"""
        app = receipt_app.ReceiptAppTerminal()
        self.assertIsNotNone(app.receipt)
        self.assertTrue(app.running)
    
    def test_print_colored(self):
        """Test colored printing doesn't crash"""
        app = receipt_app.ReceiptAppTerminal()
        # Should not raise any exceptions
        app.print_colored("Test message", "green")
        app.print_colored("Test message", "")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
