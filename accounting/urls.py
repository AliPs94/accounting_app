from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    AssociationViewSet, UserProfileViewSet, AccountViewSet,
    VoucherViewSet, VoucherDetailViewSet, DefaultAccountTemplateViewSet
)
from .auth_views import register_user, login_user, get_user_profile, switch_association
from .reports import trial_balance, income_statement, balance_sheet, general_ledger

# Create router and register viewsets
router = DefaultRouter()
router.register(r'associations', AssociationViewSet)
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'vouchers', VoucherViewSet)
router.register(r'voucher-details', VoucherDetailViewSet)
router.register(r'default-account-templates', DefaultAccountTemplateViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', register_user, name='register_user'),
    path('auth/login/', login_user, name='login_user'),
    path('auth/profile/', get_user_profile, name='get_user_profile'),
    path('auth/switch-association/', switch_association, name='switch_association'),
    
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Reports endpoints
    path('reports/trial-balance/', trial_balance, name='trial_balance'),
    path('reports/income-statement/', income_statement, name='income_statement'),
    path('reports/balance-sheet/', balance_sheet, name='balance_sheet'),
    path('reports/general-ledger/', general_ledger, name='general_ledger'),
    
    # API endpoints
    path('', include(router.urls)),
]
