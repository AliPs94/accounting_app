from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounting.models import Association, UserProfile, Account


class Command(BaseCommand):
    help = 'Create sample data for the accounting application'

    def handle(self, *args, **options):
        # Create sample association
        association, created = Association.objects.get_or_create(
            name="Sample Association",
            defaults={'name': 'Sample Association'}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created association: {association.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Association already exists: {association.name}')
            )

        # Create sample user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created user: {user.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'User already exists: {user.username}')
            )

        # Create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'association': association}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created user profile for: {user.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'User profile already exists for: {user.username}')
            )

        # Create sample chart of accounts
        sample_accounts = [
            # Assets
            {'code': '1000', 'name': 'Cash', 'account_type': 'Asset'},
            {'code': '1100', 'name': 'Accounts Receivable', 'account_type': 'Asset'},
            {'code': '1200', 'name': 'Inventory', 'account_type': 'Asset'},
            {'code': '1300', 'name': 'Equipment', 'account_type': 'Asset'},
            
            # Liabilities
            {'code': '2000', 'name': 'Accounts Payable', 'account_type': 'Liability'},
            {'code': '2100', 'name': 'Accrued Expenses', 'account_type': 'Liability'},
            {'code': '2200', 'name': 'Notes Payable', 'account_type': 'Liability'},
            
            # Equity
            {'code': '3000', 'name': 'Owner\'s Equity', 'account_type': 'Equity'},
            {'code': '3100', 'name': 'Retained Earnings', 'account_type': 'Equity'},
            
            # Revenue
            {'code': '4000', 'name': 'Sales Revenue', 'account_type': 'Revenue'},
            {'code': '4100', 'name': 'Service Revenue', 'account_type': 'Revenue'},
            
            # Expenses
            {'code': '5000', 'name': 'Cost of Goods Sold', 'account_type': 'Expense'},
            {'code': '5100', 'name': 'Operating Expenses', 'account_type': 'Expense'},
            {'code': '5200', 'name': 'Administrative Expenses', 'account_type': 'Expense'},
        ]

        created_count = 0
        for account_data in sample_accounts:
            account, created = Account.objects.get_or_create(
                code=account_data['code'],
                association=association,
                defaults={
                    'name': account_data['name'],
                    'account_type': account_data['account_type']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} new accounts')
        )

        self.stdout.write(
            self.style.SUCCESS('Sample data setup completed successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now login with username: admin, password: admin123')
        )

