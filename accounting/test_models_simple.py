from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError
from accounting.models import (
    Association, UserProfile, Account, Voucher, VoucherDetail, DefaultAccountTemplate
)


class AssociationModelTest(TestCase):
    """Test cases for Association model"""
    
    def test_create_association(self):
        """Test creating a basic association"""
        association = Association.objects.create(name="Test Company")
        self.assertEqual(association.name, "Test Company")
        self.assertIsNotNone(association.id)
        self.assertEqual(str(association), "Test Company")
    
    def test_association_ordering(self):
        """Test that associations are ordered by name"""
        Association.objects.create(name="Z Company")
        Association.objects.create(name="A Company")
        Association.objects.create(name="M Company")
        
        associations = list(Association.objects.all())
        self.assertEqual(associations[0].name, "A Company")
        self.assertEqual(associations[1].name, "M Company")
        self.assertEqual(associations[2].name, "Z Company")
    
    def test_association_unique_name(self):
        """Test that association names must be unique"""
        Association.objects.create(name="Unique Company")
        with self.assertRaises(IntegrityError):
            Association.objects.create(name="Unique Company")


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.association = Association.objects.create(name="Test Company")
    
    def test_create_user_profile(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(user=self.user, association=self.association)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.association, self.association)
        self.assertEqual(str(profile), "testuser - Test Company")
    
    def test_user_profile_unique_constraint(self):
        """Test that user can only have one profile per association"""
        UserProfile.objects.create(user=self.user, association=self.association)
        
        # Should not be able to create another profile for same user-association
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user, association=self.association)
    
    def test_user_can_have_only_one_profile(self):
        """Test that user can have only one profile due to OneToOneField"""
        # Create first profile
        profile1 = UserProfile.objects.create(user=self.user, association=self.association)
        
        # Try to create another profile for the same user should fail
        association2 = Association.objects.create(name="Company 2")
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user, association=association2)


class AccountModelTest(TestCase):
    """Test cases for Account model"""
    
    def setUp(self):
        self.association = Association.objects.create(name="Test Company")
    
    def test_create_account(self):
        """Test creating a basic account"""
        account = Account.objects.create(
            association=self.association,
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        self.assertEqual(account.name, "Cash Account")
        self.assertEqual(account.account_type, "Asset")
        self.assertEqual(account.code, "1000")
        self.assertTrue(account.is_active)
        self.assertEqual(str(account), "1000 - Cash Account")
    
    def test_account_validation_parent_same_association(self):
        """Test that parent account must belong to same association"""
        association2 = Association.objects.create(name="Company 2")
        
        parent_account = Account.objects.create(
            association=self.association,
            name="Parent Account",
            account_type="Asset",
            code="1000"
        )
        
        # Try to create child account with different association
        child_account = Account(
            association=association2,
            name="Child Account",
            account_type="Asset",
            code="1001",
            parent=parent_account
        )
        
        with self.assertRaises(ValidationError):
            child_account.clean()
    
    def test_account_unique_code_per_association(self):
        """Test that account codes must be unique within an association"""
        Account.objects.create(
            association=self.association,
            name="Account 1",
            account_type="Asset",
            code="1000"
        )
        
        # Should not be able to create another account with same code in same association
        with self.assertRaises(IntegrityError):
            Account.objects.create(
                association=self.association,
                name="Account 2",
                account_type="Liability",
                code="1000"
            )
    
    def test_account_can_have_same_code_different_associations(self):
        """Test that accounts can have same code in different associations"""
        association2 = Association.objects.create(name="Company 2")
        
        account1 = Account.objects.create(
            association=self.association,
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        account2 = Account.objects.create(
            association=association2,
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        self.assertEqual(account1.code, account2.code)
        self.assertNotEqual(account1.association, account2.association)


class VoucherModelTest(TestCase):
    """Test cases for Voucher model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.association = Association.objects.create(name="Test Company")
    
    def test_create_voucher(self):
        """Test creating a basic voucher"""
        voucher = Voucher.objects.create(
            association=self.association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=self.user
        )
        
        self.assertEqual(str(voucher.date), "2024-01-01")
        self.assertEqual(voucher.description, "Test voucher")
        self.assertEqual(voucher.voucher_type, "Journal")
        self.assertEqual(voucher.voucher_number, "JV001")
        self.assertEqual(voucher.created_by, self.user)
        self.assertEqual(str(voucher), "JV001 - Test voucher")
    
    def test_voucher_balance_calculation(self):
        """Test voucher balance calculations"""
        # Create accounts
        cash_account = Account.objects.create(
            association=self.association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        revenue_account = Account.objects.create(
            association=self.association,
            name="Revenue",
            account_type="Revenue",
            code="4000"
        )
        
        # Create voucher
        voucher = Voucher.objects.create(
            association=self.association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=self.user
        )
        
        # Create voucher details
        VoucherDetail.objects.create(
            voucher=voucher,
            account=cash_account,
            debit=Decimal("100.00"),
            credit=Decimal("0.00"),
            description="Cash received"
        )
        
        VoucherDetail.objects.create(
            voucher=voucher,
            account=revenue_account,
            debit=Decimal("0.00"),
            credit=Decimal("100.00"),
            description="Revenue earned"
        )
        
        self.assertEqual(voucher.get_total_debits(), Decimal("100.00"))
        self.assertEqual(voucher.get_total_credits(), Decimal("100.00"))
        self.assertTrue(voucher.is_balanced())


class VoucherDetailModelTest(TestCase):
    """Test cases for VoucherDetail model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.association = Association.objects.create(name="Test Company")
        
        self.account = Account.objects.create(
            association=self.association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        self.voucher = Voucher.objects.create(
            association=self.association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=self.user
        )
    
    def test_create_voucher_detail(self):
        """Test creating a voucher detail"""
        detail = VoucherDetail.objects.create(
            voucher=self.voucher,
            account=self.account,
            debit=Decimal("100.00"),
            credit=Decimal("0.00"),
            description="Cash received"
        )
        
        self.assertEqual(detail.voucher, self.voucher)
        self.assertEqual(detail.account, self.account)
        self.assertEqual(detail.debit, Decimal("100.00"))
        self.assertEqual(detail.credit, Decimal("0.00"))
        self.assertEqual(detail.description, "Cash received")
    
    def test_voucher_detail_validation_both_debit_credit(self):
        """Test that voucher detail cannot have both debit and credit"""
        detail = VoucherDetail(
            voucher=self.voucher,
            account=self.account,
            debit=Decimal("100.00"),
            credit=Decimal("50.00"),
            description="Invalid entry"
        )
        
        with self.assertRaises(ValidationError):
            detail.clean()
    
    def test_voucher_detail_validation_negative_amounts(self):
        """Test that voucher detail cannot have negative amounts"""
        detail = VoucherDetail(
            voucher=self.voucher,
            account=self.account,
            debit=Decimal("-100.00"),
            credit=Decimal("0.00"),
            description="Negative debit"
        )
        
        with self.assertRaises(ValidationError):
            detail.clean()
    
    def test_voucher_detail_validation_zero_amounts(self):
        """Test that voucher detail must have either debit or credit"""
        detail = VoucherDetail(
            voucher=self.voucher,
            account=self.account,
            debit=Decimal("0.00"),
            credit=Decimal("0.00"),
            description="Zero amounts"
        )
        
        with self.assertRaises(ValidationError):
            detail.clean()


class DefaultAccountTemplateModelTest(TestCase):
    """Test cases for DefaultAccountTemplate model"""
    
    def test_create_default_account_template(self):
        """Test creating a default account template"""
        template = DefaultAccountTemplate.objects.create(
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        self.assertEqual(template.name, "Cash Account")
        self.assertEqual(template.account_type, "Asset")
        self.assertEqual(template.code, "1000")
        self.assertTrue(template.is_active)
        self.assertEqual(str(template), "1000 - Cash Account")
    
    def test_default_account_template_hierarchy(self):
        """Test creating hierarchical default account templates"""
        parent_template = DefaultAccountTemplate.objects.create(
            name="Assets",
            account_type="Asset",
            code="1000"
        )
        
        child_template = DefaultAccountTemplate.objects.create(
            name="Cash",
            account_type="Asset",
            code="1001",
            parent=parent_template
        )
        
        self.assertEqual(child_template.parent, parent_template)
        self.assertEqual(parent_template.sub_templates.count(), 1)
        self.assertEqual(parent_template.sub_templates.first(), child_template)
