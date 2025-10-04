from django.core.management.base import BaseCommand
from django.db import transaction
from accounting.models import Association, Account, DefaultAccountTemplate


class Command(BaseCommand):
    help = 'Set up default accounts for all associations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--association-id',
            type=int,
            help='Set up default accounts for a specific association only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force setup even if association already has accounts',
        )

    def handle(self, *args, **options):
        # Create default account templates if they don't exist
        self.create_default_templates()
        
        # Get associations to process
        if options['association_id']:
            associations = Association.objects.filter(id=options['association_id'])
        else:
            associations = Association.objects.all()
        
        if not associations.exists():
            self.stdout.write(
                self.style.WARNING('No associations found.')
            )
            return
        
        for association in associations:
            self.setup_default_accounts_for_association(association, options['force'])
    
    def create_default_templates(self):
        """Create default account templates"""
        default_accounts = [
            # Assets
            {'code': '1000', 'name': 'Cash', 'account_type': 'Asset', 'parent': None},
            {'code': '1100', 'name': 'Accounts Receivable', 'account_type': 'Asset', 'parent': None},
            {'code': '1200', 'name': 'Inventory', 'account_type': 'Asset', 'parent': None},
            {'code': '1300', 'name': 'Prepaid Expenses', 'account_type': 'Asset', 'parent': None},
            {'code': '1400', 'name': 'Equipment', 'account_type': 'Asset', 'parent': None},
            {'code': '1500', 'name': 'Accumulated Depreciation - Equipment', 'account_type': 'Asset', 'parent': None},
            
            # Liabilities
            {'code': '2000', 'name': 'Accounts Payable', 'account_type': 'Liability', 'parent': None},
            {'code': '2100', 'name': 'Accrued Expenses', 'account_type': 'Liability', 'parent': None},
            {'code': '2200', 'name': 'Notes Payable', 'account_type': 'Liability', 'parent': None},
            {'code': '2300', 'name': 'Taxes Payable', 'account_type': 'Liability', 'parent': None},
            
            # Equity
            {'code': '3000', 'name': 'Owner\'s Equity', 'account_type': 'Equity', 'parent': None},
            {'code': '3100', 'name': 'Retained Earnings', 'account_type': 'Equity', 'parent': None},
            
            # Revenue
            {'code': '4000', 'name': 'Sales Revenue', 'account_type': 'Revenue', 'parent': None},
            {'code': '4100', 'name': 'Service Revenue', 'account_type': 'Revenue', 'parent': None},
            {'code': '4200', 'name': 'Interest Income', 'account_type': 'Revenue', 'parent': None},
            
            # Expenses
            {'code': '5000', 'name': 'Cost of Goods Sold', 'account_type': 'Expense', 'parent': None},
            {'code': '5100', 'name': 'Salaries and Wages', 'account_type': 'Expense', 'parent': None},
            {'code': '5200', 'name': 'Rent Expense', 'account_type': 'Expense', 'parent': None},
            {'code': '5300', 'name': 'Utilities Expense', 'account_type': 'Expense', 'parent': None},
            {'code': '5400', 'name': 'Office Supplies', 'account_type': 'Expense', 'parent': None},
            {'code': '5500', 'name': 'Depreciation Expense', 'account_type': 'Expense', 'parent': None},
            {'code': '5600', 'name': 'Insurance Expense', 'account_type': 'Expense', 'parent': None},
            {'code': '5700', 'name': 'Professional Fees', 'account_type': 'Expense', 'parent': None},
            {'code': '5800', 'name': 'Travel Expense', 'account_type': 'Expense', 'parent': None},
            {'code': '5900', 'name': 'Miscellaneous Expense', 'account_type': 'Expense', 'parent': None},
        ]
        
        created_count = 0
        for account_data in default_accounts:
            template, created = DefaultAccountTemplate.objects.get_or_create(
                code=account_data['code'],
                defaults={
                    'name': account_data['name'],
                    'account_type': account_data['account_type'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} default account templates.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Default account templates already exist.')
            )
    
    def setup_default_accounts_for_association(self, association, force=False):
        """Set up default accounts for a specific association"""
        existing_accounts = Account.objects.filter(association=association)
        
        if existing_accounts.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Association "{association.name}" already has {existing_accounts.count()} accounts. '
                    'Use --force to override.'
                )
            )
            return
        
        if force and existing_accounts.exists():
            self.stdout.write(
                self.style.WARNING(f'Deleting existing accounts for "{association.name}"...')
            )
            existing_accounts.delete()
        
        # Get all default templates
        templates = DefaultAccountTemplate.objects.filter(is_active=True).order_by('code')
        
        if not templates.exists():
            self.stdout.write(
                self.style.ERROR('No default account templates found. Run this command first.')
            )
            return
        
        created_accounts = []
        
        with transaction.atomic():
            # Create accounts in order (parents first)
            for template in templates:
                account = Account.objects.create(
                    association=association,
                    name=template.name,
                    account_type=template.account_type,
                    code=template.code,
                    is_active=template.is_active
                )
                created_accounts.append(account)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Created {len(created_accounts)} default accounts for "{association.name}"'
            )
        )
