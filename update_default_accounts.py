"""
Script to update default account templates
Run with: python manage.py shell < update_default_accounts.py
"""

from accounting.models import DefaultAccountTemplate

# Example 1: Update an existing account
template = DefaultAccountTemplate.objects.filter(code='1000').first()
if template:
    template.name = 'Cash on Hand'  # Change name
    template.save()
    print(f"Updated: {template.code} - {template.name}")

# Example 2: Add a new default account
new_account, created = DefaultAccountTemplate.objects.get_or_create(
    code='1610',
    defaults={
        'name': 'Buildings',
        'account_type': 'Asset',
        'is_active': True
    }
)
if created:
    print(f"Created new account: {new_account.code} - {new_account.name}")
else:
    print(f"Account already exists: {new_account.code} - {new_account.name}")

# Example 3: Deactivate an account (won't be used for new associations)
template = DefaultAccountTemplate.objects.filter(code='5900').first()
if template:
    template.is_active = False
    template.save()
    print(f"Deactivated: {template.code} - {template.name}")

print("\nAll default account templates:")
for template in DefaultAccountTemplate.objects.all().order_by('code'):
    status = "✓" if template.is_active else "✗"
    print(f"{status} {template.code} - {template.name} ({template.account_type})")

