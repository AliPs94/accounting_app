from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Association, UserProfile, Account, Voucher, VoucherDetail, DefaultAccountTemplate


class AssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Association
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    association_name = serializers.CharField(source='association.name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'association', 'username', 'association_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class AccountSerializer(serializers.ModelSerializer):
    association_name = serializers.CharField(source='association.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    sub_accounts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'association', 'association_name', 'name', 'account_type', 
            'parent', 'parent_name', 'code', 'is_active', 'sub_accounts_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'association', 'created_at', 'updated_at', 'sub_accounts_count']
    
    def get_sub_accounts_count(self, obj):
        return obj.sub_accounts.count()
    
    def validate(self, data):
        """Validate that parent account belongs to same association"""
        parent = data.get('parent')
        
        # During creation, association comes from perform_create, not from data
        # During update, get association from the instance
        if self.instance:
            association = self.instance.association
        else:
            # For creation, we'll validate in the view's perform_create
            # or get it from context if provided
            association = self.context.get('association')
        
        if parent and association and parent.association != association:
            raise serializers.ValidationError(
                "Parent account must belong to the same association."
            )
        
        return data


class VoucherDetailSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    account_code = serializers.CharField(source='account.code', read_only=True)
    
    class Meta:
        model = VoucherDetail
        fields = [
            'id', 'account', 'account_name', 'account_code', 
            'debit', 'credit', 'description'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate that a detail line cannot have both debit and credit"""
        debit = data.get('debit', 0)
        credit = data.get('credit', 0)
        
        if debit > 0 and credit > 0:
            raise serializers.ValidationError(
                "A voucher detail cannot have both debit and credit amounts."
            )
        if debit < 0 or credit < 0:
            raise serializers.ValidationError(
                "Debit and credit amounts cannot be negative."
            )
        if debit == 0 and credit == 0:
            raise serializers.ValidationError(
                "A voucher detail must have either a debit or credit amount."
            )
        
        return data


class VoucherSerializer(serializers.ModelSerializer):
    association_name = serializers.CharField(source='association.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    details = VoucherDetailSerializer(many=True, required=False)
    total_debits = serializers.SerializerMethodField()
    total_credits = serializers.SerializerMethodField()
    is_balanced = serializers.SerializerMethodField()
    
    class Meta:
        model = Voucher
        fields = [
            'id', 'association', 'association_name', 'date', 'description', 
            'voucher_type', 'voucher_number', 'created_by', 'created_by_username',
            'details', 'total_debits', 'total_credits', 'is_balanced',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'association', 'created_by', 'created_at', 'updated_at', 
            'total_debits', 'total_credits', 'is_balanced'
        ]
    
    def get_total_debits(self, obj):
        return obj.get_total_debits()
    
    def get_total_credits(self, obj):
        return obj.get_total_credits()
    
    def get_is_balanced(self, obj):
        return obj.is_balanced()
    
    def create(self, validated_data):
        """Create voucher with nested details"""
        details_data = validated_data.pop('details', [])
        voucher = Voucher.objects.create(**validated_data)
        
        for detail_data in details_data:
            VoucherDetail.objects.create(voucher=voucher, **detail_data)
        
        # Validate that the voucher is balanced
        if not voucher.is_balanced():
            voucher.delete()
            raise serializers.ValidationError(
                "Voucher must be balanced: total debits must equal total credits."
            )
        
        return voucher
    
    def update(self, instance, validated_data):
        """Update voucher with nested details"""
        details_data = validated_data.pop('details', [])
        
        # Update voucher fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update details
        if details_data:
            # Delete existing details
            instance.details.all().delete()
            
            # Create new details
            for detail_data in details_data:
                VoucherDetail.objects.create(voucher=instance, **detail_data)
        
        # Validate that the voucher is balanced
        if not instance.is_balanced():
            raise serializers.ValidationError(
                "Voucher must be balanced: total debits must equal total credits."
            )
        
        return instance


class VoucherListSerializer(serializers.ModelSerializer):
    """Simplified serializer for voucher list view"""
    association_name = serializers.CharField(source='association.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    total_debits = serializers.SerializerMethodField()
    total_credits = serializers.SerializerMethodField()
    details_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Voucher
        fields = [
            'id', 'association_name', 'date', 'description', 
            'voucher_type', 'voucher_number', 'created_by_username',
            'total_debits', 'total_credits', 'details_count', 'created_at'
        ]
    
    def get_total_debits(self, obj):
        return obj.get_total_debits()
    
    def get_total_credits(self, obj):
        return obj.get_total_credits()
    
    def get_details_count(self, obj):
        return obj.details.count()


class DefaultAccountTemplateSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    sub_templates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DefaultAccountTemplate
        fields = [
            'id', 'name', 'account_type', 'parent', 'parent_name', 
            'code', 'is_active', 'sub_templates_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'sub_templates_count']
    
    def get_sub_templates_count(self, obj):
        return obj.sub_templates.count()
    
    def validate(self, data):
        """Validate that parent template belongs to same account type or is None"""
        parent = data.get('parent')
        account_type = data.get('account_type')
        
        if parent and parent.account_type != account_type:
            raise serializers.ValidationError(
                "Parent template must have the same account type."
            )
        
        return data

