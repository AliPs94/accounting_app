from django.contrib import admin
from .models import Association, UserProfile, Account, Voucher, VoucherDetail, DefaultAccountTemplate


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'association', 'created_at']
    list_filter = ['association']
    search_fields = ['user__username', 'association__name']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'association', 'is_active']
    list_filter = ['account_type', 'association', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['association', 'code']


class VoucherDetailInline(admin.TabularInline):
    model = VoucherDetail
    extra = 1


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['voucher_number', 'date', 'voucher_type', 'association', 'created_by']
    list_filter = ['voucher_type', 'association', 'date']
    search_fields = ['voucher_number', 'description']
    inlines = [VoucherDetailInline]
    ordering = ['-date', '-created_at']


@admin.register(VoucherDetail)
class VoucherDetailAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'account', 'debit', 'credit', 'description']
    list_filter = ['account__account_type', 'voucher__association']
    search_fields = ['voucher__voucher_number', 'account__name']


@admin.register(DefaultAccountTemplate)
class DefaultAccountTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'parent', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']
    list_editable = ['is_active']  # Allow quick activation/deactivation
