from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Association(models.Model):
    """Represents each tenant company/association"""
    name = models.CharField(max_length=200, unique=True, verbose_name=_("Name"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")


class UserProfile(models.Model):
    """Links users to their associations for multi-tenancy"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    association = models.ForeignKey(Association, on_delete=models.CASCADE, verbose_name=_("Association"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.user.username} - {self.association.name}"

    class Meta:
        unique_together = ['user', 'association']
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")


class Account(models.Model):
    """Chart of accounts model"""
    ACCOUNT_TYPE_CHOICES = [
        ('Asset', _('Asset')),
        ('Liability', _('Liability')),
        ('Equity', _('Equity')),
        ('Revenue', _('Revenue')),
        ('Expense', _('Expense')),
    ]

    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='accounts', verbose_name=_("Association"))
    name = models.CharField(max_length=200, verbose_name=_("Account Name"))
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, verbose_name=_("Account Type"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_accounts', verbose_name=_("Parent Account"))
    code = models.CharField(max_length=50, verbose_name=_("Account Code"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        """Validate that parent account belongs to same association"""
        if self.parent and self.parent.association != self.association:
            raise ValidationError("Parent account must belong to the same association.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['code']
        unique_together = ['association', 'code']
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")


class Voucher(models.Model):
    """Journal voucher header"""
    VOUCHER_TYPE_CHOICES = [
        ('Payment', _('Payment')),
        ('Receipt', _('Receipt')),
        ('Journal', _('Journal')),
    ]

    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='vouchers', verbose_name=_("Association"))
    date = models.DateField(verbose_name=_("Date"))
    description = models.TextField(verbose_name=_("Description"))
    voucher_type = models.CharField(max_length=20, choices=VOUCHER_TYPE_CHOICES, verbose_name=_("Voucher Type"))
    voucher_number = models.CharField(max_length=50, verbose_name=_("Voucher Number"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Created By"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.voucher_number} - {self.description[:50]}"

    def get_total_debits(self):
        """Calculate total debits for this voucher"""
        return sum(detail.debit for detail in self.details.all())

    def get_total_credits(self):
        """Calculate total credits for this voucher"""
        return sum(detail.credit for detail in self.details.all())

    def is_balanced(self):
        """Check if voucher is balanced (debits = credits)"""
        return self.get_total_debits() == self.get_total_credits()

    def clean(self):
        """Validate voucher balance"""
        if self.pk:  # Only validate if voucher exists (has details)
            if not self.is_balanced():
                raise ValidationError("Voucher must be balanced: total debits must equal total credits.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @staticmethod
    def get_next_voucher_number(association, voucher_type):
        """Get the next suggested voucher number for a given association and voucher type"""
        last_voucher = Voucher.objects.filter(
            association=association,
            voucher_type=voucher_type
        ).order_by('-voucher_number').first()
        
        if last_voucher:
            # Try to extract numeric part from the voucher number
            import re
            match = re.search(r'(\d+)$', last_voucher.voucher_number)
            if match:
                last_number = int(match.group(1))
                # Reconstruct with incremented number
                prefix = last_voucher.voucher_number[:match.start()]
                next_number = last_number + 1
                # Preserve the zero-padding
                number_width = len(match.group(1))
                return f"{prefix}{next_number:0{number_width}d}"
            else:
                # If no number found, append -1
                return f"{last_voucher.voucher_number}-1"
        else:
            # First voucher of this type for this association
            # Return a default suggestion based on type
            type_prefix = {
                'Payment': 'PAY-',
                'Receipt': 'REC-',
                'Journal': 'JV-'
            }
            return f"{type_prefix.get(voucher_type, 'V-')}001"

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['association', 'voucher_type', 'voucher_number']
        verbose_name = _("Voucher")
        verbose_name_plural = _("Vouchers")


class VoucherDetail(models.Model):
    """Individual debit/credit lines in a voucher"""
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='details', verbose_name=_("Voucher"))
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name=_("Account"))
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("Debit"))
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name=_("Credit"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.voucher.voucher_number} - {self.account.name} - Dr: {self.debit} Cr: {self.credit}"

    def clean(self):
        """Validate that a detail line cannot have both debit and credit"""
        if self.debit > 0 and self.credit > 0:
            raise ValidationError("A voucher detail cannot have both debit and credit amounts.")
        if self.debit < 0 or self.credit < 0:
            raise ValidationError("Debit and credit amounts cannot be negative.")
        if self.debit == 0 and self.credit == 0:
            raise ValidationError("A voucher detail must have either a debit or credit amount.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['id']
        verbose_name = _("Voucher Detail")
        verbose_name_plural = _("Voucher Details")


class DefaultAccountTemplate(models.Model):
    """Template for default accounts that will be created for new associations"""
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    account_type = models.CharField(max_length=20, choices=Account.ACCOUNT_TYPE_CHOICES, verbose_name=_("Account Type"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_templates', verbose_name=_("Parent"))
    code = models.CharField(max_length=50, verbose_name=_("Code"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']
        verbose_name = _("Default Account Template")
        verbose_name_plural = _("Default Account Templates")
