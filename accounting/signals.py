from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Association, Account, DefaultAccountTemplate


@receiver(post_save, sender=Association)
def create_default_accounts_for_new_association(sender, instance, created, **kwargs):
    """Automatically create default accounts when a new association is created"""
    if created:
        # Get all default account templates
        templates = DefaultAccountTemplate.objects.filter(is_active=True).order_by('code')
        
        if templates.exists():
            with transaction.atomic():
                # Create accounts from templates
                for template in templates:
                    Account.objects.create(
                        association=instance,
                        name=template.name,
                        account_type=template.account_type,
                        code=template.code,
                        is_active=template.is_active
                    )
