from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError
from accounting.models import (
    Association, UserProfile, Account, Voucher, VoucherDetail, DefaultAccountTemplate
)


class TestAssociation(TestCase):
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
        assert associations[0].name == "A Company"
        assert associations[1].name == "M Company"
        assert associations[2].name == "Z Company"
    
    def test_association_unique_name(self):
        """Test that association names must be unique"""
        Association.objects.create(name="Unique Company")
        with pytest.raises(IntegrityError):
            Association.objects.create(name="Unique Company")


@pytest.mark.django_db
class TestUserProfile:
    """Test cases for UserProfile model"""
    
    def test_create_user_profile(self):
        """Test creating a user profile"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        profile = UserProfile.objects.create(user=user, association=association)
        assert profile.user == user
        assert profile.association == association
        assert str(profile) == "testuser - Test Company"
    
    def test_user_profile_unique_constraint(self):
        """Test that user can only have one profile per association"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        UserProfile.objects.create(user=user, association=association)
        
        # Should not be able to create another profile for same user-association
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user, association=association)
    
    def test_user_can_have_multiple_profiles_different_associations(self):
        """Test that user can have profiles in different associations"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association1 = Association.objects.create(name="Company 1")
        association2 = Association.objects.create(name="Company 2")
        
        profile1 = UserProfile.objects.create(user=user, association=association1)
        profile2 = UserProfile.objects.create(user=user, association=association2)
        
        assert profile1.association == association1
        assert profile2.association == association2


@pytest.mark.django_db
class TestAccount:
    """Test cases for Account model"""
    
    def test_create_account(self):
        """Test creating a basic account"""
        association = Association.objects.create(name="Test Company")
        account = Account.objects.create(
            association=association,
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        assert account.name == "Cash Account"
        assert account.account_type == "Asset"
        assert account.code == "1000"
        assert account.is_active is True
        assert str(account) == "1000 - Cash Account"
    
    def test_account_validation_parent_same_association(self):
        """Test that parent account must belong to same association"""
        association1 = Association.objects.create(name="Company 1")
        association2 = Association.objects.create(name="Company 2")
        
        parent_account = Account.objects.create(
            association=association1,
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
        
        with pytest.raises(ValidationError):
            child_account.clean()
    
    def test_account_unique_code_per_association(self):
        """Test that account codes must be unique within an association"""
        association = Association.objects.create(name="Test Company")
        
        Account.objects.create(
            association=association,
            name="Account 1",
            account_type="Asset",
            code="1000"
        )
        
        # Should not be able to create another account with same code in same association
        with pytest.raises(IntegrityError):
            Account.objects.create(
                association=association,
                name="Account 2",
                account_type="Liability",
                code="1000"
            )
    
    def test_account_can_have_same_code_different_associations(self):
        """Test that accounts can have same code in different associations"""
        association1 = Association.objects.create(name="Company 1")
        association2 = Association.objects.create(name="Company 2")
        
        account1 = Account.objects.create(
            association=association1,
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
        
        assert account1.code == account2.code
        assert account1.association != account2.association


@pytest.mark.django_db
class TestVoucher:
    """Test cases for Voucher model"""
    
    def test_create_voucher(self):
        """Test creating a basic voucher"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user
        )
        
        assert voucher.date.strftime("%Y-%m-%d") == "2024-01-01"
        assert voucher.description == "Test voucher"
        assert voucher.voucher_type == "Journal"
        assert voucher.voucher_number == "JV001"
        assert voucher.created_by == user
        assert str(voucher) == "JV001 - Test voucher"
    
    def test_voucher_balance_calculation(self):
        """Test voucher balance calculations"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        # Create accounts
        cash_account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        revenue_account = Account.objects.create(
            association=association,
            name="Revenue",
            account_type="Revenue",
            code="4000"
        )
        
        # Create voucher
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user
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
        
        assert voucher.get_total_debits() == Decimal("100.00")
        assert voucher.get_total_credits() == Decimal("100.00")
        assert voucher.is_balanced() is True
    
    def test_voucher_balance_validation(self):
        """Test that unbalanced vouchers raise validation error"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        cash_account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user
        )
        
        # Create unbalanced voucher detail
        VoucherDetail.objects.create(
            voucher=voucher,
            account=cash_account,
            debit=Decimal("100.00"),
            credit=Decimal("0.00"),
            description="Cash received"
        )
        
        # Should raise validation error when saving unbalanced voucher
        with pytest.raises(ValidationError):
            voucher.clean()


@pytest.mark.django_db
class TestVoucherDetail:
    """Test cases for VoucherDetail model"""
    
    def test_create_voucher_detail(self):
        """Test creating a voucher detail"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user
        )
        
        detail = VoucherDetail.objects.create(
            voucher=voucher,
            account=account,
            debit=Decimal("100.00"),
            credit=Decimal("0.00"),
            description="Cash received"
        )
        
        assert detail.voucher == voucher
        assert detail.account == account
        assert detail.debit == Decimal("100.00")
        assert detail.credit == Decimal("0.00")
        assert detail.description == "Cash received"
    
    def test_voucher_detail_validation_both_debit_credit(self):
        """Test that voucher detail cannot have both debit and credit"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user
        )
        
        detail = VoucherDetail(
            voucher=voucher,
            account=account,
            debit=Decimal("100.00"),
            credit=Decimal("50.00"),
            description="Invalid entry"
        )
        
        with pytest.raises(ValidationError):
            detail.clean()
    
    def test_voucher_detail_validation_negative_amounts(self):
        """Test that voucher detail cannot have negative amounts"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user
        )
        
        detail = VoucherDetail(
            voucher=voucher,
            account=account,
            debit=Decimal("-100.00"),
            credit=Decimal("0.00"),
            description="Negative debit"
        )
        
        with pytest.raises(ValidationError):
            detail.clean()
    
    def test_voucher_detail_validation_zero_amounts(self):
        """Test that voucher detail must have either debit or credit"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user
        )
        
        detail = VoucherDetail(
            voucher=voucher,
            account=account,
            debit=Decimal("0.00"),
            credit=Decimal("0.00"),
            description="Zero amounts"
        )
        
        with pytest.raises(ValidationError):
            detail.clean()


@pytest.mark.django_db
class TestDefaultAccountTemplate:
    """Test cases for DefaultAccountTemplate model"""
    
    def test_create_default_account_template(self):
        """Test creating a default account template"""
        template = DefaultAccountTemplate.objects.create(
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        assert template.name == "Cash Account"
        assert template.account_type == "Asset"
        assert template.code == "1000"
        assert template.is_active is True
        assert str(template) == "1000 - Cash Account"
    
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
        
        assert child_template.parent == parent_template
        assert parent_template.sub_templates.count() == 1
        assert parent_template.sub_templates.first() == child_template
