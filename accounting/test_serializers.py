import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from accounting.models import Association, UserProfile, Account, Voucher, VoucherDetail, DefaultAccountTemplate
from accounting.serializers import (
    AssociationSerializer, UserProfileSerializer, AccountSerializer,
    VoucherSerializer, VoucherDetailSerializer, DefaultAccountTemplateSerializer
)


@pytest.mark.django_db
class TestAssociationSerializer:
    """Test cases for AssociationSerializer"""
    
    def test_serialize_association(self):
        """Test serializing an association"""
        association = Association.objects.create(name="Test Company")
        serializer = AssociationSerializer(association)
        
        data = serializer.data
        assert data['name'] == "Test Company"
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_deserialize_association(self):
        """Test deserializing association data"""
        data = {'name': 'New Company'}
        serializer = AssociationSerializer(data=data)
        
        assert serializer.is_valid()
        association = serializer.save()
        assert association.name == "New Company"


@pytest.mark.django_db
class TestUserProfileSerializer:
    """Test cases for UserProfileSerializer"""
    
    def test_serialize_user_profile(self):
        """Test serializing a user profile"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        profile = UserProfile.objects.create(user=user, association=association)
        
        serializer = UserProfileSerializer(profile)
        data = serializer.data
        
        assert data['username'] == "testuser"
        assert data['association_name'] == "Test Company"
        assert data['user'] == user.id
        assert data['association'] == association.id


@pytest.mark.django_db
class TestAccountSerializer:
    """Test cases for AccountSerializer"""
    
    def test_serialize_account(self):
        """Test serializing an account"""
        association = Association.objects.create(name="Test Company")
        account = Account.objects.create(
            association=association,
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        serializer = AccountSerializer(account)
        data = serializer.data
        
        assert data['name'] == "Cash Account"
        assert data['account_type'] == "Asset"
        assert data['code'] == "1000"
        assert data['association_name'] == "Test Company"
        assert data['sub_accounts_count'] == 0
    
    def test_serialize_account_with_parent(self):
        """Test serializing an account with parent"""
        association = Association.objects.create(name="Test Company")
        parent_account = Account.objects.create(
            association=association,
            name="Assets",
            account_type="Asset",
            code="1000"
        )
        
        child_account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1001",
            parent=parent_account
        )
        
        serializer = AccountSerializer(child_account)
        data = serializer.data
        
        assert data['parent'] == parent_account.id
        assert data['parent_name'] == "Assets"
    
    def test_validate_parent_same_association(self):
        """Test validation that parent account belongs to same association"""
        association1 = Association.objects.create(name="Company 1")
        association2 = Association.objects.create(name="Company 2")
        
        parent_account = Account.objects.create(
            association=association1,
            name="Parent Account",
            account_type="Asset",
            code="1000"
        )
        
        data = {
            'association': association2.id,
            'name': 'Child Account',
            'account_type': 'Asset',
            'code': '1001',
            'parent': parent_account.id
        }
        
        serializer = AccountSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
class TestVoucherDetailSerializer:
    """Test cases for VoucherDetailSerializer"""
    
    def test_serialize_voucher_detail(self):
        """Test serializing a voucher detail"""
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
        
        serializer = VoucherDetailSerializer(detail)
        data = serializer.data
        
        assert data['account'] == account.id
        assert data['account_name'] == "Cash"
        assert data['account_code'] == "1000"
        assert float(data['debit']) == 100.00
        assert float(data['credit']) == 0.00
        assert data['description'] == "Cash received"
    
    def test_validate_both_debit_credit(self):
        """Test validation that detail cannot have both debit and credit"""
        data = {
            'account': 1,
            'debit': 100.00,
            'credit': 50.00,
            'description': 'Invalid entry'
        }
        
        serializer = VoucherDetailSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
    
    def test_validate_negative_amounts(self):
        """Test validation that amounts cannot be negative"""
        data = {
            'account': 1,
            'debit': -100.00,
            'credit': 0.00,
            'description': 'Negative debit'
        }
        
        serializer = VoucherDetailSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
    
    def test_validate_zero_amounts(self):
        """Test validation that detail must have either debit or credit"""
        data = {
            'account': 1,
            'debit': 0.00,
            'credit': 0.00,
            'description': 'Zero amounts'
        }
        
        serializer = VoucherDetailSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
class TestVoucherSerializer:
    """Test cases for VoucherSerializer"""
    
    def test_serialize_voucher(self):
        """Test serializing a voucher"""
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
        
        serializer = VoucherSerializer(voucher)
        data = serializer.data
        
        assert data['description'] == "Test voucher"
        assert data['voucher_type'] == "Journal"
        assert data['voucher_number'] == "JV001"
        assert data['association_name'] == "Test Company"
        assert data['created_by_username'] == "testuser"
        assert data['total_debits'] == 0
        assert data['total_credits'] == 0
        assert data['is_balanced'] is True
    
    def test_serialize_voucher_with_details(self):
        """Test serializing a voucher with details"""
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
        
        VoucherDetail.objects.create(
            voucher=voucher,
            account=account,
            debit=Decimal("100.00"),
            credit=Decimal("0.00"),
            description="Cash received"
        )
        
        serializer = VoucherSerializer(voucher)
        data = serializer.data
        
        assert len(data['details']) == 1
        assert data['details'][0]['account'] == account.id
        assert float(data['details'][0]['debit']) == 100.00
        assert data['total_debits'] == 100.00
        assert data['total_credits'] == 0.00
        assert data['is_balanced'] is False
    
    def test_create_balanced_voucher(self):
        """Test creating a balanced voucher"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
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
        
        data = {
            'date': '2024-01-01',
            'description': 'Test voucher',
            'voucher_type': 'Journal',
            'voucher_number': 'JV001',
            'details': [
                {
                    'account': cash_account.id,
                    'debit': 100.00,
                    'credit': 0.00,
                    'description': 'Cash received'
                },
                {
                    'account': revenue_account.id,
                    'debit': 0.00,
                    'credit': 100.00,
                    'description': 'Revenue earned'
                }
            ]
        }
        
        serializer = VoucherSerializer(data=data)
        assert serializer.is_valid()
        voucher = serializer.save(association=association, created_by=user)
        
        assert voucher.details.count() == 2
        assert voucher.is_balanced() is True
    
    def test_create_unbalanced_voucher_fails(self):
        """Test that creating an unbalanced voucher fails"""
        user = User.objects.create_user(username="testuser", password="testpass")
        association = Association.objects.create(name="Test Company")
        
        cash_account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        data = {
            'date': '2024-01-01',
            'description': 'Test voucher',
            'voucher_type': 'Journal',
            'voucher_number': 'JV001',
            'details': [
                {
                    'account': cash_account.id,
                    'debit': 100.00,
                    'credit': 0.00,
                    'description': 'Cash received'
                }
            ]
        }
        
        serializer = VoucherSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
class TestDefaultAccountTemplateSerializer:
    """Test cases for DefaultAccountTemplateSerializer"""
    
    def test_serialize_default_account_template(self):
        """Test serializing a default account template"""
        template = DefaultAccountTemplate.objects.create(
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        serializer = DefaultAccountTemplateSerializer(template)
        data = serializer.data
        
        assert data['name'] == "Cash Account"
        assert data['account_type'] == "Asset"
        assert data['code'] == "1000"
        assert data['is_active'] is True
        assert data['sub_templates_count'] == 0
    
    def test_serialize_template_with_parent(self):
        """Test serializing a template with parent"""
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
        
        serializer = DefaultAccountTemplateSerializer(child_template)
        data = serializer.data
        
        assert data['parent'] == parent_template.id
        assert data['parent_name'] == "Assets"
    
    def test_validate_parent_same_account_type(self):
        """Test validation that parent template has same account type"""
        parent_template = DefaultAccountTemplate.objects.create(
            name="Assets",
            account_type="Asset",
            code="1000"
        )
        
        data = {
            'name': 'Revenue Account',
            'account_type': 'Revenue',
            'code': '4000',
            'parent': parent_template.id
        }
        
        serializer = DefaultAccountTemplateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
