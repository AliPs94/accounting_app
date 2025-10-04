from django.test import TestCase
from django.contrib.auth.models import User
from .models import Association, UserProfile, Account


class BasicTestCase(TestCase):
    """Basic test to verify Django setup works"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.association = Association.objects.create(name='Test Company')
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            association=self.association
        )
    
    def test_association_creation(self):
        """Test association model creation"""
        self.assertEqual(self.association.name, 'Test Company')
        self.assertTrue(self.association.id is not None)
    
    def test_user_profile_creation(self):
        """Test user profile model creation"""
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.association, self.association)
    
    def test_account_creation(self):
        """Test account model creation"""
        account = Account.objects.create(
            association=self.association,
            name='Cash Account',
            account_type='Asset',
            code='1000'
        )
        self.assertEqual(account.name, 'Cash Account')
        self.assertEqual(account.account_type, 'Asset')
        self.assertEqual(account.code, '1000')
