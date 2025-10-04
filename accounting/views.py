from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Association, UserProfile, Account, Voucher, VoucherDetail, DefaultAccountTemplate
from .serializers import (
    AssociationSerializer, UserProfileSerializer, AccountSerializer,
    VoucherSerializer, VoucherListSerializer, VoucherDetailSerializer,
    DefaultAccountTemplateSerializer
)


class AssociationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing associations"""
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter associations based on user's profile"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            return Association.objects.filter(id=user_profile.association.id)
        return Association.objects.none()
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all associations for selection purposes"""
        associations = Association.objects.all()
        serializer = self.get_serializer(associations, many=True)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter profiles based on user's association"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            return UserProfile.objects.filter(association=user_profile.association)
        return UserProfile.objects.none()


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chart of accounts"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter accounts based on user's association"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            return Account.objects.filter(association=user_profile.association)
        return Account.objects.none()
    
    def perform_create(self, serializer):
        """Set association from user's profile"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            serializer.save(association=user_profile.association)
        else:
            raise PermissionError("User must be associated with an organization.")
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get accounts filtered by account type"""
        account_type = request.query_params.get('type')
        if account_type:
            queryset = self.get_queryset().filter(account_type=account_type)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'Account type parameter is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get accounts in hierarchical structure"""
        queryset = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class VoucherViewSet(viewsets.ModelViewSet):
    """ViewSet for managing journal vouchers"""
    queryset = Voucher.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return VoucherListSerializer
        return VoucherSerializer
    
    def get_queryset(self):
        """Filter vouchers based on user's association"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            return Voucher.objects.filter(association=user_profile.association)
        return Voucher.objects.none()
    
    def perform_create(self, serializer):
        """Set association and created_by from user's profile"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            serializer.save(
                association=user_profile.association,
                created_by=self.request.user
            )
        else:
            raise PermissionError("User must be associated with an organization.")
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get vouchers within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Both start_date and end_date parameters are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get vouchers filtered by voucher type"""
        voucher_type = request.query_params.get('type')
        if voucher_type:
            queryset = self.get_queryset().filter(voucher_type=voucher_type)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'Voucher type parameter is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def next_voucher_number(self, request):
        """Get the next suggested voucher number for a given voucher type"""
        voucher_type = request.query_params.get('type')
        if not voucher_type:
            return Response(
                {'error': 'Voucher type parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate voucher type
        valid_types = [choice[0] for choice in Voucher.VOUCHER_TYPE_CHOICES]
        if voucher_type not in valid_types:
            return Response(
                {'error': f'Invalid voucher type. Must be one of: {", ".join(valid_types)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if not user_profile:
            return Response(
                {'error': 'User must be associated with an organization'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        next_number = Voucher.get_next_voucher_number(
            user_profile.association, 
            voucher_type
        )
        
        return Response({
            'voucher_type': voucher_type,
            'suggested_number': next_number
        })
    
    @action(detail=True, methods=['get'])
    def trial_balance(self, request, pk=None):
        """Generate trial balance for a specific voucher"""
        voucher = self.get_object()
        details = voucher.details.all()
        
        trial_balance_data = []
        for detail in details:
            trial_balance_data.append({
                'account_code': detail.account.code,
                'account_name': detail.account.name,
                'account_type': detail.account.account_type,
                'debit': float(detail.debit),
                'credit': float(detail.credit),
            })
        
        return Response({
            'voucher_number': voucher.voucher_number,
            'date': voucher.date,
            'description': voucher.description,
            'trial_balance': trial_balance_data,
            'total_debits': float(voucher.get_total_debits()),
            'total_credits': float(voucher.get_total_credits()),
            'is_balanced': voucher.is_balanced()
        })


class VoucherDetailViewSet(viewsets.ModelViewSet):
    """ViewSet for managing voucher details"""
    queryset = VoucherDetail.objects.all()
    serializer_class = VoucherDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter voucher details based on user's association"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            return VoucherDetail.objects.filter(
                voucher__association=user_profile.association
            )
        return VoucherDetail.objects.none()
    
    def perform_create(self, serializer):
        """Validate that the voucher belongs to user's association"""
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        if user_profile:
            voucher = serializer.validated_data['voucher']
            if voucher.association != user_profile.association:
                raise PermissionError("Voucher does not belong to your organization.")
            serializer.save()
        else:
            raise PermissionError("User must be associated with an organization.")


class DefaultAccountTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing default account templates"""
    queryset = DefaultAccountTemplate.objects.all()
    serializer_class = DefaultAccountTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def apply_to_association(self, request):
        """Apply default account templates to a specific association"""
        association_id = request.data.get('association_id')
        if not association_id:
            return Response(
                {'error': 'association_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            association = Association.objects.get(id=association_id)
        except Association.DoesNotExist:
            return Response(
                {'error': 'Association not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all active templates
        templates = DefaultAccountTemplate.objects.filter(is_active=True).order_by('code')
        
        if not templates.exists():
            return Response(
                {'error': 'No default account templates found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if association already has accounts
        existing_accounts = Account.objects.filter(association=association)
        if existing_accounts.exists():
            return Response(
                {'error': 'Association already has accounts. Delete existing accounts first.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create accounts from templates
        created_accounts = []
        for template in templates:
            account = Account.objects.create(
                association=association,
                name=template.name,
                account_type=template.account_type,
                code=template.code,
                is_active=template.is_active
            )
            created_accounts.append(account)
        
        return Response({
            'message': f'Successfully created {len(created_accounts)} default accounts',
            'accounts_created': len(created_accounts)
        })
