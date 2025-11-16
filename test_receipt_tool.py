#!/usr/bin/env python3
"""Test suite for receipt_tool.py"""

import os
import sys
import tempfile
import unittest
import json
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

import receipt_tool


class TestProduct(unittest.TestCase):
    """Test Product class"""
    
    def test_product_creation(self):
        """Test creating a product"""
        product = receipt_tool.Product("Test Item", 2, 10.0)
        self.assertEqual(product.name, "Test Item")
        self.assertEqual(product.quantity, 2)
        self.assertEqual(product.price, 10.0)
    
    def test_product_total(self):
        """Test product total calculation"""
        product = receipt_tool.Product("Test Item", 3, 15.5)
        self.assertEqual(product.total(), 46.5)
    
    def test_product_to_dict(self):
        """Test product to dictionary conversion"""
        product = receipt_tool.Product("Test Item", 2, 10.0)
        data = product.to_dict()
        self.assertEqual(data["name"], "Test Item")
        self.assertEqual(data["quantity"], 2)
        self.assertEqual(data["price"], 10.0)
    
    def test_product_from_dict(self):
        """Test product from dictionary"""
        data = {"name": "Test Item", "quantity": 3, "price": 12.5}
        product = receipt_tool.Product.from_dict(data)
        self.assertEqual(product.name, "Test Item")
        self.assertEqual(product.quantity, 3)
        self.assertEqual(product.price, 12.5)


class TestReceipt(unittest.TestCase):
    """Test Receipt class"""
    
    def setUp(self):
        """Set up test receipt"""
        # Use a temporary config for testing
        self.test_config = receipt_tool.DEFAULT_CONFIG.copy()
        self.receipt = receipt_tool.Receipt(config=self.test_config)
    
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
        self.assertIn("ALV", text)
        self.assertIn("YHTEENSÄ", text)
    
    def test_get_logo(self):
        """Test getting logo"""
        logo = self.receipt.get_logo()
        self.assertIsInstance(logo, str)
        self.assertIn("HARJUN RASKASKONE OY", logo)
    
    def test_set_logo(self):
        """Test setting logo"""
        new_logo = "*** TEST LOGO ***\n*** LINE 2 ***"
        result = self.receipt.set_logo(new_logo)
        self.assertTrue(result)
        # Note: actual config save would happen, but we're using test config
    
    def test_cleanup_text(self):
        """Test control character cleanup"""
        text_with_controls = "Hello\x00World\x01Test\nNewline\tTab"
        cleaned = self.receipt._cleanup_text(text_with_controls)
        # Should keep \n and \t, remove other control chars
        self.assertIn("\n", cleaned)
        self.assertIn("\t", cleaned)
        self.assertNotIn("\x00", cleaned)
        self.assertNotIn("\x01", cleaned)
    
    def test_validate_logo(self):
        """Test logo validation"""
        # Valid logo (within width)
        valid_logo = "Short logo"
        self.assertTrue(self.receipt._validate_logo(valid_logo))
        
        # Invalid logo (too wide)
        invalid_logo = "X" * (self.receipt.width + 20)
        self.assertFalse(self.receipt._validate_logo(invalid_logo))
    
    def test_manual_override(self):
        """Test manual text override"""
        self.receipt.add_product("Item", 1, 10.0)
        
        # Normal generation
        normal_text = self.receipt.generate_text()
        self.assertIn("Item", normal_text)
        
        # Set override
        override_text = "CUSTOM RECEIPT TEXT"
        self.receipt.set_manual_override(override_text)
        overridden = self.receipt.generate_text()
        self.assertEqual(overridden, override_text)
        
        # Clear override
        self.receipt.set_manual_override(None)
        cleared_text = self.receipt.generate_text()
        self.assertIn("Item", cleared_text)
    
    def test_to_dict(self):
        """Test receipt to dictionary"""
        self.receipt.add_product("Item 1", 2, 50.0)
        data = self.receipt.to_dict()
        
        self.assertIn("products", data)
        self.assertIn("totals", data)
        self.assertEqual(len(data["products"]), 1)
        self.assertEqual(data["totals"]["subtotal"], 100.0)
    
    def test_template_support(self):
        """Test template functionality"""
        # Default template
        self.assertEqual(self.receipt.current_template, "default")
        
        # Switch template
        self.receipt.current_template = "minimal"
        text = self.receipt.generate_text()
        self.assertIsInstance(text, str)


class TestReceiptExporter(unittest.TestCase):
    """Test ReceiptExporter class"""
    
    def setUp(self):
        """Set up test receipt"""
        self.receipt = receipt_tool.Receipt()
        self.receipt.add_product("Test Product", 1, 10.0)
    
    def test_export_txt(self):
        """Test TXT export"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
        
        try:
            result = receipt_tool.ReceiptExporter.export_txt(self.receipt, temp_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            
            # Check content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("Test Product", content)
            self.assertIn("10.00", content)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_pdf(self):
        """Test PDF export"""
        if not receipt_tool.REPORTLAB_AVAILABLE:
            self.skipTest("reportlab not available")
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
        
        try:
            result = receipt_tool.ReceiptExporter.export_pdf(self.receipt, temp_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            
            # Check file size
            size = os.path.getsize(temp_path)
            self.assertGreater(size, 100)  # PDF should be at least 100 bytes
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestReceiptToolCLI(unittest.TestCase):
    """Test CLI functionality"""
    
    def test_cli_creation(self):
        """Test creating CLI instance"""
        cli = receipt_tool.ReceiptToolCLI()
        self.assertIsNotNone(cli.receipt)
    
    def test_smoke_test(self):
        """Test smoke test functionality"""
        # This should run without errors
        result = receipt_tool.ReceiptToolCLI.smoke_test()
        self.assertEqual(result, 0)


class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = receipt_tool.DEFAULT_CONFIG
        self.assertIn("logo_ascii", config)
        self.assertIn("width", config)
        self.assertIn("vat_rate", config)
        self.assertIn("company_info", config)
        self.assertIn("templates", config)
    
    def test_config_structure(self):
        """Test configuration structure"""
        config = receipt_tool.DEFAULT_CONFIG
        
        # Check company info
        company = config["company_info"]
        self.assertIn("name", company)
        self.assertIn("business_id", company)
        self.assertIn("address", company)
        self.assertIn("phone", company)
        
        # Check templates
        templates = config["templates"]
        self.assertIn("default", templates)
        self.assertIn("minimal", templates)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
