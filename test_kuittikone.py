#!/usr/bin/env python3
"""Test suite for kuittikone.py"""

import os
import sys
import tempfile
import unittest
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

import kuittikone


class TestPaymentCardPreset(unittest.TestCase):
    """Test PaymentCardPreset class"""
    
    def test_card_preset_creation(self):
        """Test creating a card preset"""
        preset = kuittikone.PaymentCardPreset(
            card_type=kuittikone.CardType.VISA,
            enabled=True,
            name="Visa",
            fee_percentage=0.0
        )
        self.assertEqual(preset.card_type, kuittikone.CardType.VISA)
        self.assertTrue(preset.enabled)
        self.assertEqual(preset.name, "Visa")
    
    def test_card_preset_to_dict(self):
        """Test card preset to dictionary conversion"""
        preset = kuittikone.PaymentCardPreset(
            card_type=kuittikone.CardType.MASTERCARD,
            enabled=True,
            name="MasterCard",
            fee_percentage=1.5
        )
        data = preset.to_dict()
        self.assertEqual(data["card_type"], "mastercard")
        self.assertEqual(data["name"], "MasterCard")
        self.assertEqual(data["fee_percentage"], 1.5)
    
    def test_card_preset_from_dict(self):
        """Test card preset from dictionary"""
        data = {
            "card_type": "amex",
            "enabled": True,
            "name": "American Express",
            "fee_percentage": 2.0,
            "description": "Amex cards",
            "icon": "💳"
        }
        preset = kuittikone.PaymentCardPreset.from_dict(data)
        self.assertEqual(preset.card_type, kuittikone.CardType.AMEX)
        self.assertEqual(preset.fee_percentage, 2.0)


class TestWarrantyInfo(unittest.TestCase):
    """Test WarrantyInfo class"""
    
    def test_warranty_creation(self):
        """Test creating warranty info"""
        warranty = kuittikone.WarrantyInfo(
            serial_number="TEST-001",
            purchase_date=datetime.now().isoformat(),
            warranty_months=12,
            product_name="Test Product"
        )
        self.assertEqual(warranty.serial_number, "TEST-001")
        self.assertEqual(warranty.warranty_months, 12)
    
    def test_warranty_valid(self):
        """Test warranty validity check"""
        # Valid warranty
        warranty = kuittikone.WarrantyInfo(
            serial_number="TEST-001",
            purchase_date=datetime.now().isoformat(),
            warranty_months=12,
            product_name="Test Product"
        )
        self.assertTrue(warranty.is_warranty_valid())
        
        # Expired warranty
        old_date = (datetime.now() - timedelta(days=400)).isoformat()
        expired_warranty = kuittikone.WarrantyInfo(
            serial_number="TEST-002",
            purchase_date=old_date,
            warranty_months=12,
            product_name="Old Product"
        )
        self.assertFalse(expired_warranty.is_warranty_valid())
    
    def test_return_valid(self):
        """Test return period validity"""
        warranty = kuittikone.WarrantyInfo(
            serial_number="TEST-001",
            purchase_date=datetime.now().isoformat(),
            warranty_months=12,
            product_name="Test Product",
            return_days=14
        )
        self.assertTrue(warranty.is_return_valid())
        
        # Expired return period
        old_date = (datetime.now() - timedelta(days=20)).isoformat()
        expired = kuittikone.WarrantyInfo(
            serial_number="TEST-002",
            purchase_date=old_date,
            warranty_months=12,
            product_name="Old Product",
            return_days=14
        )
        self.assertFalse(expired.is_return_valid())
    
    def test_warranty_text(self):
        """Test warranty text generation"""
        warranty = kuittikone.WarrantyInfo(
            serial_number="TEST-001",
            purchase_date=datetime.now().isoformat(),
            warranty_months=12,
            product_name="Test Product",
            notes="Test note"
        )
        text = warranty.warranty_text()
        self.assertIn("TEST-001", text)
        self.assertIn("Test Product", text)
        self.assertIn("Test note", text)


class TestPromoRule(unittest.TestCase):
    """Test PromoRule class"""
    
    def test_promo_rule_creation(self):
        """Test creating promo rule"""
        rule = kuittikone.PromoRule(
            rule_id="promo1",
            description="Test promo",
            condition_type="amount_over",
            condition_value=50.0,
            action_type="add_line",
            action_value="Get 10% off"
        )
        self.assertEqual(rule.rule_id, "promo1")
        self.assertEqual(rule.condition_value, 50.0)
        self.assertTrue(rule.enabled)
    
    def test_promo_rule_serialization(self):
        """Test promo rule to/from dict"""
        rule = kuittikone.PromoRule(
            rule_id="promo2",
            description="Card promo",
            condition_type="card_type",
            condition_value="visa",
            action_type="add_bonus_code",
            action_value="VISA2025"
        )
        data = rule.to_dict()
        restored = kuittikone.PromoRule.from_dict(data)
        self.assertEqual(rule.rule_id, restored.rule_id)
        self.assertEqual(rule.condition_value, restored.condition_value)


class TestReceiptLayout(unittest.TestCase):
    """Test ReceiptLayout class"""
    
    def test_default_layout(self):
        """Test default layout creation"""
        layout = kuittikone.ReceiptLayout()
        self.assertTrue(layout.show_logo)
        self.assertTrue(layout.show_header)
        self.assertTrue(layout.show_products)
        self.assertTrue(layout.show_totals)
    
    def test_custom_layout(self):
        """Test custom layout configuration"""
        layout = kuittikone.ReceiptLayout(
            show_logo=False,
            show_warranty=True,
            header_font=kuittikone.FontStyle.BOLD_BIG
        )
        self.assertFalse(layout.show_logo)
        self.assertTrue(layout.show_warranty)
        self.assertEqual(layout.header_font, kuittikone.FontStyle.BOLD_BIG)
    
    def test_layout_serialization(self):
        """Test layout to/from dict"""
        layout = kuittikone.ReceiptLayout(
            show_vat_breakdown=False,
            footer_font=kuittikone.FontStyle.SLIM
        )
        data = layout.to_dict()
        restored = kuittikone.ReceiptLayout.from_dict(data)
        self.assertFalse(restored.show_vat_breakdown)
        self.assertEqual(restored.footer_font, kuittikone.FontStyle.SLIM)


class TestCompanyPreset(unittest.TestCase):
    """Test CompanyPreset class"""
    
    def test_preset_creation(self):
        """Test creating company preset"""
        preset = kuittikone.CompanyPreset(
            preset_id="test_company",
            company_name="Test Company Oy",
            business_id="FI12345678",
            address="Test Street 1",
            phone="+358 40 123 4567",
            email="test@example.com"
        )
        self.assertEqual(preset.preset_id, "test_company")
        self.assertEqual(preset.company_name, "Test Company Oy")
        self.assertTrue(preset.enabled)
    
    def test_default_payment_presets(self):
        """Test default payment presets are created"""
        preset = kuittikone.CompanyPreset(
            preset_id="test",
            company_name="Test",
            business_id="FI123",
            address="Addr",
            phone="123",
            email="test@test.com"
        )
        self.assertIsNotNone(preset.payment_presets)
        self.assertGreater(len(preset.payment_presets), 0)
        
        # Check for default card types
        card_types = [p.card_type for p in preset.payment_presets]
        self.assertIn(kuittikone.CardType.VISA, card_types)
        self.assertIn(kuittikone.CardType.MASTERCARD, card_types)
    
    def test_preset_serialization(self):
        """Test preset to/from dict"""
        preset = kuittikone.CompanyPreset(
            preset_id="serialize_test",
            company_name="Serialize Test Oy",
            business_id="FI99999999",
            address="Serialize St 1",
            phone="+358 50 999 9999",
            email="serialize@test.com",
            template_type=kuittikone.TemplateType.MINIMAL,
            vat_rate=0.24
        )
        
        data = preset.to_dict()
        restored = kuittikone.CompanyPreset.from_dict(data)
        
        self.assertEqual(preset.preset_id, restored.preset_id)
        self.assertEqual(preset.company_name, restored.company_name)
        self.assertEqual(preset.template_type, restored.template_type)
        self.assertEqual(preset.vat_rate, restored.vat_rate)


class TestASCIILogoEncoder(unittest.TestCase):
    """Test ASCIILogoEncoder class"""
    
    def test_simple_style(self):
        """Test simple ASCII style"""
        result = kuittikone.ASCIILogoEncoder.text_to_ascii_art("TEST", "normal")
        self.assertIn("TEST", result)
        self.assertIn("=", result)
    
    def test_block_style(self):
        """Test block ASCII style"""
        result = kuittikone.ASCIILogoEncoder.text_to_ascii_art("TEST", "block")
        self.assertIn("TEST", result)
        self.assertIn("╔", result)
        self.assertIn("╚", result)
    
    def test_banner_style(self):
        """Test banner ASCII style"""
        result = kuittikone.ASCIILogoEncoder.text_to_ascii_art("TEST", "banner")
        self.assertIn("TEST", result)
        self.assertIn("*", result)
    
    def test_epson_escpos(self):
        """Test EPSON ESC/POS conversion"""
        result = kuittikone.ASCIILogoEncoder.to_epson_escpos("TEST LOGO")
        self.assertIn("TEST LOGO", result)
        # Check for ESC/POS commands (escape characters)
        self.assertIn("\x1B", result)


class TestFontEngine(unittest.TestCase):
    """Test FontEngine class"""
    
    def test_get_font_info(self):
        """Test getting font information"""
        info = kuittikone.FontEngine.get_font_info(kuittikone.FontStyle.BOLD_BIG)
        self.assertIsNotNone(info)
        self.assertIn("char_width", info)
        self.assertIn("line_height", info)
    
    def test_apply_normal_font(self):
        """Test applying normal font"""
        text = "TEST"
        result = kuittikone.FontEngine.apply_font(text, kuittikone.FontStyle.NORMAL)
        self.assertEqual(text, result)
    
    def test_apply_bold_font(self):
        """Test applying bold/big font"""
        text = "TEST"
        result = kuittikone.FontEngine.apply_font(text, kuittikone.FontStyle.BOLD_BIG)
        self.assertNotEqual(text, result)
        # Bold big should space out characters
        self.assertGreater(len(result), len(text))


class TestKuittikoneManager(unittest.TestCase):
    """Test KuittikoneManager class"""
    
    def setUp(self):
        """Set up test manager with temporary config file"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.manager = kuittikone.KuittikoneManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary files"""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_manager_creation(self):
        """Test creating manager"""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.config)
    
    def test_add_preset(self):
        """Test adding company preset"""
        preset = kuittikone.CompanyPreset(
            preset_id="test_add",
            company_name="Add Test Oy",
            business_id="FI111",
            address="Add St",
            phone="123",
            email="add@test.com"
        )
        result = self.manager.add_company_preset(preset)
        self.assertTrue(result)
        
        # Verify it was saved
        retrieved = self.manager.get_company_preset("test_add")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.company_name, "Add Test Oy")
    
    def test_list_presets(self):
        """Test listing presets"""
        # Add multiple presets
        for i in range(3):
            preset = kuittikone.CompanyPreset(
                preset_id=f"test_{i}",
                company_name=f"Test Company {i}",
                business_id=f"FI{i}",
                address="Addr",
                phone="123",
                email="test@test.com"
            )
            self.manager.add_company_preset(preset)
        
        presets = self.manager.list_presets()
        self.assertEqual(len(presets), 3)
    
    def test_delete_preset(self):
        """Test deleting preset"""
        preset = kuittikone.CompanyPreset(
            preset_id="test_delete",
            company_name="Delete Test",
            business_id="FI999",
            address="Del St",
            phone="123",
            email="del@test.com"
        )
        self.manager.add_company_preset(preset)
        
        result = self.manager.delete_preset("test_delete")
        self.assertTrue(result)
        
        # Verify it was deleted
        retrieved = self.manager.get_company_preset("test_delete")
        self.assertIsNone(retrieved)
    
    def test_switch_preset(self):
        """Test switching between presets"""
        preset1 = kuittikone.CompanyPreset(
            preset_id="preset1",
            company_name="Company 1",
            business_id="FI1",
            address="A",
            phone="1",
            email="1@test.com"
        )
        preset2 = kuittikone.CompanyPreset(
            preset_id="preset2",
            company_name="Company 2",
            business_id="FI2",
            address="B",
            phone="2",
            email="2@test.com"
        )
        
        self.manager.add_company_preset(preset1)
        self.manager.add_company_preset(preset2)
        
        result = self.manager.switch_preset("preset2")
        self.assertTrue(result)
        self.assertEqual(self.manager.current_preset_id, "preset2")
        
        current = self.manager.get_current_preset()
        self.assertEqual(current.company_name, "Company 2")
    
    def test_add_warranty(self):
        """Test adding warranty information"""
        warranty = kuittikone.WarrantyInfo(
            serial_number="WARRANT-001",
            purchase_date=datetime.now().isoformat(),
            warranty_months=24,
            product_name="Test Product"
        )
        
        result = self.manager.add_warranty(warranty)
        self.assertTrue(result)
        
        # Verify it was saved
        retrieved = self.manager.get_warranty("WARRANT-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.product_name, "Test Product")
        self.assertEqual(retrieved.warranty_months, 24)
    
    def test_generate_receipt(self):
        """Test generating receipt"""
        # Add a preset
        preset = kuittikone.CompanyPreset(
            preset_id="receipt_test",
            company_name="Receipt Test Oy",
            business_id="FI12345",
            address="Test Street 1",
            phone="+358 40 123 4567",
            email="receipt@test.com"
        )
        self.manager.add_company_preset(preset)
        self.manager.switch_preset("receipt_test")
        
        # Generate receipt
        products = [
            {"name": "Product 1", "quantity": 2, "price": 10.0},
            {"name": "Product 2", "quantity": 1, "price": 25.0}
        ]
        
        receipt = self.manager.generate_receipt(
            products=products,
            payment_method=kuittikone.PaymentMethod.CARD,
            card_type=kuittikone.CardType.VISA
        )
        
        self.assertIsNotNone(receipt)
        self.assertIn("Receipt Test Oy", receipt)
        self.assertIn("Product 1", receipt)
        self.assertIn("Product 2", receipt)
        self.assertIn("YHTEENSÄ", receipt)
    
    def test_receipt_with_warranty(self):
        """Test receipt generation with warranty info"""
        preset = kuittikone.CompanyPreset(
            preset_id="warranty_test",
            company_name="Warranty Test",
            business_id="FI999",
            address="Addr",
            phone="123",
            email="test@test.com"
        )
        preset.layout.show_warranty = True
        self.manager.add_company_preset(preset)
        self.manager.switch_preset("warranty_test")
        
        # Add warranty
        warranty = kuittikone.WarrantyInfo(
            serial_number="TEST-W-001",
            purchase_date=datetime.now().isoformat(),
            warranty_months=12,
            product_name="Test Product"
        )
        self.manager.add_warranty(warranty)
        
        # Generate receipt
        products = [{"name": "Test Product", "quantity": 1, "price": 100.0}]
        receipt = self.manager.generate_receipt(
            products=products,
            payment_method=kuittikone.PaymentMethod.CASH,
            serial_numbers=["TEST-W-001"]
        )
        
        self.assertIn("TAKUUTIEDOT", receipt)
        self.assertIn("TEST-W-001", receipt)
    
    def test_receipt_with_promo(self):
        """Test receipt with promotional rules"""
        preset = kuittikone.CompanyPreset(
            preset_id="promo_test",
            company_name="Promo Test",
            business_id="FI888",
            address="Addr",
            phone="123",
            email="test@test.com"
        )
        
        # Add promo rule
        preset.promo_rules.append(kuittikone.PromoRule(
            rule_id="test_promo",
            description="Over 50€",
            condition_type="amount_over",
            condition_value=50.0,
            action_type="add_line",
            action_value="🎁 Get 10% off next purchase!"
        ))
        
        self.manager.add_company_preset(preset)
        self.manager.switch_preset("promo_test")
        
        # Generate receipt with amount over 50
        products = [{"name": "Expensive Item", "quantity": 1, "price": 100.0}]
        receipt = self.manager.generate_receipt(
            products=products,
            payment_method=kuittikone.PaymentMethod.CARD
        )
        
        self.assertIn("TARJOUKSET", receipt)
        self.assertIn("Get 10% off", receipt)
    
    def test_backup_restore(self):
        """Test backup and restore functionality"""
        # Add some data
        preset = kuittikone.CompanyPreset(
            preset_id="backup_test",
            company_name="Backup Test Oy",
            business_id="FI777",
            address="Backup St",
            phone="123",
            email="backup@test.com"
        )
        self.manager.add_company_preset(preset)
        
        warranty = kuittikone.WarrantyInfo(
            serial_number="BACKUP-001",
            purchase_date=datetime.now().isoformat(),
            warranty_months=12,
            product_name="Backup Product"
        )
        self.manager.add_warranty(warranty)
        
        # Backup
        backup_dir = tempfile.mkdtemp()
        result = self.manager.backup_to_usb(backup_dir)
        self.assertTrue(result)
        
        # Find backup file
        backup_files = list(Path(backup_dir).glob("kuittikone_backup_*.json"))
        self.assertEqual(len(backup_files), 1)
        
        # Create new manager and restore
        new_manager = kuittikone.KuittikoneManager(tempfile.NamedTemporaryFile(suffix='.json', delete=False).name)
        result = new_manager.restore_from_usb(str(backup_files[0]))
        self.assertTrue(result)
        
        # Verify data was restored
        restored_preset = new_manager.get_company_preset("backup_test")
        self.assertIsNotNone(restored_preset)
        self.assertEqual(restored_preset.company_name, "Backup Test Oy")
        
        restored_warranty = new_manager.get_warranty("BACKUP-001")
        self.assertIsNotNone(restored_warranty)
        self.assertEqual(restored_warranty.product_name, "Backup Product")


class TestDefaultPresets(unittest.TestCase):
    """Test default preset creation"""
    
    def test_create_default_presets(self):
        """Test creating default presets"""
        presets = kuittikone.create_default_presets()
        self.assertIsNotNone(presets)
        self.assertGreater(len(presets), 0)
        
        # Check HRK preset exists
        hrk_preset = next((p for p in presets if p.preset_id == "hrk_default"), None)
        self.assertIsNotNone(hrk_preset)
        self.assertEqual(hrk_preset.company_name, "Harjun Raskaskone Oy")


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow from setup to receipt generation"""
        # Create manager
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        manager = kuittikone.KuittikoneManager(temp_file.name)
        
        try:
            # Add presets
            for preset in kuittikone.create_default_presets():
                manager.add_company_preset(preset)
            
            # Add warranty
            warranty = kuittikone.WarrantyInfo(
                serial_number="INT-TEST-001",
                purchase_date=datetime.now().isoformat(),
                warranty_months=12,
                product_name="Integration Test Product"
            )
            manager.add_warranty(warranty)
            
            # Switch preset
            manager.switch_preset("hrk_default")
            
            # Generate receipt
            products = [
                {"name": "Kaivinkone", "quantity": 1, "price": 850.0},
                {"name": "Nosturi", "quantity": 1, "price": 1200.0}
            ]
            
            receipt = manager.generate_receipt(
                products=products,
                payment_method=kuittikone.PaymentMethod.CARD,
                card_type=kuittikone.CardType.MASTERCARD,
                serial_numbers=["INT-TEST-001"]
            )
            
            # Verify receipt contents
            self.assertIn("Harjun Raskaskone Oy", receipt)
            self.assertIn("Kaivinkone", receipt)
            self.assertIn("Nosturi", receipt)
            self.assertIn("YHTEENSÄ", receipt)
            self.assertIn("MasterCard", receipt)
            
            # Test backup
            backup_dir = tempfile.mkdtemp()
            backup_result = manager.backup_to_usb(backup_dir)
            self.assertTrue(backup_result)
            
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass


if __name__ == "__main__":
    unittest.main()
