import pytest
import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounting.models import Association, UserProfile, Account, Voucher, VoucherDetail, DefaultAccountTemplate


@pytest.fixture
def api_client():
    """Create API client for testing"""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def association():
    """Create a test association"""
    return Association.objects.create(name="Test Company")


@pytest.fixture
def user_profile(user, association):
    """Create a user profile linking user to association"""
    return UserProfile.objects.create(user=user, association=association)


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client"""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.mark.django_db
class TestAssociationViewSet:
    """Test cases for AssociationViewSet"""
    
    def test_list_associations_authenticated(self, authenticated_client, user_profile):
        """Test listing associations for authenticated user"""
        url = reverse('association-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == "Test Company"
    
    def test_list_associations_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list associations"""
        url = reverse('association-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_all_associations(self, authenticated_client, association):
        """Test getting all associations for selection"""
        url = reverse('association-all')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == "Test Company"
    
    def test_create_association(self, authenticated_client, user_profile):
        """Test creating a new association"""
        url = reverse('association-list')
        data = {'name': 'New Company'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Company'
        assert Association.objects.filter(name='New Company').exists()
    
    def test_update_association(self, authenticated_client, user_profile, association):
        """Test updating an association"""
        url = reverse('association-detail', kwargs={'pk': association.id})
        data = {'name': 'Updated Company'}
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Company'
        association.refresh_from_db()
        assert association.name == 'Updated Company'


@pytest.mark.django_db
class TestAccountViewSet:
    """Test cases for AccountViewSet"""
    
    def test_list_accounts_authenticated(self, authenticated_client, user_profile, association):
        """Test listing accounts for authenticated user"""
        Account.objects.create(
            association=association,
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        url = reverse('account-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == "Cash Account"
    
    def test_list_accounts_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list accounts"""
        url = reverse('account-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_account(self, authenticated_client, user_profile, association):
        """Test creating a new account"""
        url = reverse('account-list')
        data = {
            'name': 'New Account',
            'account_type': 'Asset',
            'code': '2000'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Account'
        assert Account.objects.filter(name='New Account').exists()
    
    def test_get_accounts_by_type(self, authenticated_client, user_profile, association):
        """Test getting accounts filtered by type"""
        Account.objects.create(
            association=association,
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        Account.objects.create(
            association=association,
            name="Revenue Account",
            account_type="Revenue",
            code="4000"
        )
        
        url = reverse('account-by-type')
        response = authenticated_client.get(url, {'type': 'Asset'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['account_type'] == 'Asset'
    
    def test_get_accounts_hierarchy(self, authenticated_client, user_profile, association):
        """Test getting accounts in hierarchical structure"""
        parent_account = Account.objects.create(
            association=association,
            name="Assets",
            account_type="Asset",
            code="1000"
        )
        
        Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1001",
            parent=parent_account
        )
        
        url = reverse('account-hierarchy')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # Only parent accounts
        assert response.data[0]['name'] == "Assets"


@pytest.mark.django_db
class TestVoucherViewSet:
    """Test cases for VoucherViewSet"""
    
    def test_list_vouchers_authenticated(self, authenticated_client, user_profile, association):
        """Test listing vouchers for authenticated user"""
        Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user_profile.user
        )
        
        url = reverse('voucher-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['description'] == "Test voucher"
    
    def test_create_voucher(self, authenticated_client, user_profile, association):
        """Test creating a new voucher"""
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
        
        url = reverse('voucher-list')
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
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['description'] == 'Test voucher'
        assert Voucher.objects.filter(voucher_number='JV001').exists()
    
    def test_get_vouchers_by_date_range(self, authenticated_client, user_profile, association):
        """Test getting vouchers within date range"""
        Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="January voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user_profile.user
        )
        
        Voucher.objects.create(
            association=association,
            date="2024-02-01",
            description="February voucher",
            voucher_type="Journal",
            voucher_number="JV002",
            created_by=user_profile.user
        )
        
        url = reverse('voucher-by-date-range')
        response = authenticated_client.get(url, {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['description'] == "January voucher"
    
    def test_get_vouchers_by_type(self, authenticated_client, user_profile, association):
        """Test getting vouchers filtered by type"""
        Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Payment voucher",
            voucher_type="Payment",
            voucher_number="PV001",
            created_by=user_profile.user
        )
        
        Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Journal voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user_profile.user
        )
        
        url = reverse('voucher-by-type')
        response = authenticated_client.get(url, {'type': 'Payment'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['voucher_type'] == 'Payment'
    
    def test_get_voucher_trial_balance(self, authenticated_client, user_profile, association):
        """Test getting trial balance for a voucher"""
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
        
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user_profile.user
        )
        
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
        
        url = reverse('voucher-trial-balance', kwargs={'pk': voucher.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['voucher_number'] == 'JV001'
        assert response.data['is_balanced'] is True
        assert len(response.data['trial_balance']) == 2


@pytest.mark.django_db
class TestVoucherDetailViewSet:
    """Test cases for VoucherDetailViewSet"""
    
    def test_list_voucher_details_authenticated(self, authenticated_client, user_profile, association):
        """Test listing voucher details for authenticated user"""
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user_profile.user
        )
        
        account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        VoucherDetail.objects.create(
            voucher=voucher,
            account=account,
            debit=Decimal("100.00"),
            credit=Decimal("0.00"),
            description="Cash received"
        )
        
        url = reverse('voucherdetail-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['description'] == "Cash received"
    
    def test_create_voucher_detail(self, authenticated_client, user_profile, association):
        """Test creating a voucher detail"""
        voucher = Voucher.objects.create(
            association=association,
            date="2024-01-01",
            description="Test voucher",
            voucher_type="Journal",
            voucher_number="JV001",
            created_by=user_profile.user
        )
        
        account = Account.objects.create(
            association=association,
            name="Cash",
            account_type="Asset",
            code="1000"
        )
        
        url = reverse('voucherdetail-list')
        data = {
            'voucher': voucher.id,
            'account': account.id,
            'debit': 100.00,
            'credit': 0.00,
            'description': 'Cash received'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['description'] == 'Cash received'
        assert VoucherDetail.objects.filter(description='Cash received').exists()


@pytest.mark.django_db
class TestDefaultAccountTemplateViewSet:
    """Test cases for DefaultAccountTemplateViewSet"""
    
    def test_list_templates_authenticated(self, authenticated_client):
        """Test listing default account templates"""
        DefaultAccountTemplate.objects.create(
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        url = reverse('defaultaccounttemplate-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == "Cash Account"
    
    def test_apply_templates_to_association(self, authenticated_client, association):
        """Test applying default account templates to an association"""
        DefaultAccountTemplate.objects.create(
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        DefaultAccountTemplate.objects.create(
            name="Revenue Account",
            account_type="Revenue",
            code="4000"
        )
        
        url = reverse('defaultaccounttemplate-apply-to-association')
        data = {'association_id': association.id}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['accounts_created'] == 2
        assert Account.objects.filter(association=association).count() == 2
    
    def test_apply_templates_to_association_with_existing_accounts(self, authenticated_client, association):
        """Test that applying templates fails if association already has accounts"""
        Account.objects.create(
            association=association,
            name="Existing Account",
            account_type="Asset",
            code="1000"
        )
        
        DefaultAccountTemplate.objects.create(
            name="Cash Account",
            account_type="Asset",
            code="1000"
        )
        
        url = reverse('defaultaccounttemplate-apply-to-association')
        data = {'association_id': association.id}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already has accounts' in response.data['error']
