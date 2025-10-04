from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import datetime, date
from .models import Account, VoucherDetail, UserProfile
from .serializers import AccountSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trial_balance(request):
    """Generate trial balance report for a date range"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'Both start_date and end_date parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user's association
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile:
        return Response(
            {'error': 'User profile not found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get all accounts for the association
    accounts = Account.objects.filter(association=user_profile.association, is_active=True)
    
    trial_balance_data = []
    
    for account in accounts:
        # Get opening balance (transactions before start_date)
        opening_debits = VoucherDetail.objects.filter(
            account=account,
            voucher__date__lt=start_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('debit'))['total'] or 0
        
        opening_credits = VoucherDetail.objects.filter(
            account=account,
            voucher__date__lt=start_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        opening_balance = opening_debits - opening_credits
        
        # Get period transactions (within date range)
        period_debits = VoucherDetail.objects.filter(
            account=account,
            voucher__date__gte=start_date,
            voucher__date__lte=end_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('debit'))['total'] or 0
        
        period_credits = VoucherDetail.objects.filter(
            account=account,
            voucher__date__gte=start_date,
            voucher__date__lte=end_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        # Calculate closing balance
        closing_balance = opening_balance + period_debits - period_credits
        
        # Only include accounts with transactions or non-zero balances
        if opening_balance != 0 or period_debits != 0 or period_credits != 0 or closing_balance != 0:
            trial_balance_data.append({
                'account_id': account.id,
                'account_code': account.code,
                'account_name': account.name,
                'account_type': account.account_type,
                'opening_balance': float(opening_balance),
                'period_debits': float(period_debits),
                'period_credits': float(period_credits),
                'closing_balance': float(closing_balance),
            })
    
    # Calculate totals
    total_opening_debits = sum(item['opening_balance'] for item in trial_balance_data if item['opening_balance'] > 0)
    total_opening_credits = sum(abs(item['opening_balance']) for item in trial_balance_data if item['opening_balance'] < 0)
    total_period_debits = sum(item['period_debits'] for item in trial_balance_data)
    total_period_credits = sum(item['period_credits'] for item in trial_balance_data)
    total_closing_debits = sum(item['closing_balance'] for item in trial_balance_data if item['closing_balance'] > 0)
    total_closing_credits = sum(abs(item['closing_balance']) for item in trial_balance_data if item['closing_balance'] < 0)
    
    return Response({
        'start_date': start_date,
        'end_date': end_date,
        'trial_balance': trial_balance_data,
        'totals': {
            'opening_debits': float(total_opening_debits),
            'opening_credits': float(total_opening_credits),
            'period_debits': float(total_period_debits),
            'period_credits': float(total_period_credits),
            'closing_debits': float(total_closing_debits),
            'closing_credits': float(total_closing_credits),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def income_statement(request):
    """Generate income statement for a date range"""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'Both start_date and end_date parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user's association
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile:
        return Response(
            {'error': 'User profile not found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get revenue accounts
    revenue_accounts = Account.objects.filter(
        association=user_profile.association,
        account_type='Revenue',
        is_active=True
    )
    
    # Get expense accounts
    expense_accounts = Account.objects.filter(
        association=user_profile.association,
        account_type='Expense',
        is_active=True
    )
    
    # Calculate revenue
    revenue_data = []
    total_revenue = 0
    
    for account in revenue_accounts:
        # For revenue accounts, credits increase revenue
        revenue_amount = VoucherDetail.objects.filter(
            account=account,
            voucher__date__gte=start_date,
            voucher__date__lte=end_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        if revenue_amount > 0:
            revenue_data.append({
                'account_code': account.code,
                'account_name': account.name,
                'amount': float(revenue_amount),
            })
            total_revenue += revenue_amount
    
    # Calculate expenses
    expense_data = []
    total_expenses = 0
    
    for account in expense_accounts:
        # For expense accounts, debits increase expenses
        expense_amount = VoucherDetail.objects.filter(
            account=account,
            voucher__date__gte=start_date,
            voucher__date__lte=end_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('debit'))['total'] or 0
        
        if expense_amount > 0:
            expense_data.append({
                'account_code': account.code,
                'account_name': account.name,
                'amount': float(expense_amount),
            })
            total_expenses += expense_amount
    
    # Calculate net income/loss
    net_income = total_revenue - total_expenses
    
    return Response({
        'start_date': start_date,
        'end_date': end_date,
        'revenue': {
            'items': revenue_data,
            'total': float(total_revenue),
        },
        'expenses': {
            'items': expense_data,
            'total': float(total_expenses),
        },
        'net_income': float(net_income),
        'is_profit': net_income > 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def balance_sheet(request):
    """Generate balance sheet for a specific date"""
    as_of_date = request.query_params.get('as_of_date')
    
    if not as_of_date:
        return Response(
            {'error': 'as_of_date parameter is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user's association
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile:
        return Response(
            {'error': 'User profile not found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get accounts by type
    asset_accounts = Account.objects.filter(
        association=user_profile.association,
        account_type='Asset',
        is_active=True
    )
    
    liability_accounts = Account.objects.filter(
        association=user_profile.association,
        account_type='Liability',
        is_active=True
    )
    
    equity_accounts = Account.objects.filter(
        association=user_profile.association,
        account_type='Equity',
        is_active=True
    )
    
    def calculate_account_balance(account, as_of_date):
        """Calculate account balance as of a specific date"""
        debits = VoucherDetail.objects.filter(
            account=account,
            voucher__date__lte=as_of_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('debit'))['total'] or 0
        
        credits = VoucherDetail.objects.filter(
            account=account,
            voucher__date__lte=as_of_date,
            voucher__association=user_profile.association
        ).aggregate(total=Sum('credit'))['total'] or 0
        
        # For assets and expenses: balance = debits - credits
        # For liabilities, equity, and revenue: balance = credits - debits
        if account.account_type in ['Asset', 'Expense']:
            return debits - credits
        else:
            return credits - debits
    
    # Calculate assets
    assets_data = []
    total_assets = 0
    
    for account in asset_accounts:
        balance = calculate_account_balance(account, as_of_date)
        if balance != 0:
            assets_data.append({
                'account_code': account.code,
                'account_name': account.name,
                'balance': float(balance),
            })
            total_assets += balance
    
    # Calculate liabilities
    liabilities_data = []
    total_liabilities = 0
    
    for account in liability_accounts:
        balance = calculate_account_balance(account, as_of_date)
        if balance != 0:
            liabilities_data.append({
                'account_code': account.code,
                'account_name': account.name,
                'balance': float(balance),
            })
            total_liabilities += balance
    
    # Calculate equity
    equity_data = []
    total_equity = 0
    
    for account in equity_accounts:
        balance = calculate_account_balance(account, as_of_date)
        if balance != 0:
            equity_data.append({
                'account_code': account.code,
                'account_name': account.name,
                'balance': float(balance),
            })
            total_equity += balance
    
    # Calculate total equity and liabilities
    total_equity_and_liabilities = total_liabilities + total_equity
    
    return Response({
        'as_of_date': as_of_date,
        'assets': {
            'items': assets_data,
            'total': float(total_assets),
        },
        'liabilities': {
            'items': liabilities_data,
            'total': float(total_liabilities),
        },
        'equity': {
            'items': equity_data,
            'total': float(total_equity),
        },
        'total_equity_and_liabilities': float(total_equity_and_liabilities),
        'is_balanced': abs(total_assets - total_equity_and_liabilities) < 0.01,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def general_ledger(request):
    """Generate general ledger report for a specific account within a date range"""
    account_id = request.query_params.get('account_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not account_id or not start_date or not end_date:
        return Response(
            {'error': 'account_id, start_date, and end_date parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        account_id = int(account_id)
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid parameter format. Use account_id as integer and dates as YYYY-MM-DD'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user's association
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile:
        return Response(
            {'error': 'User profile not found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify account belongs to user's association
    try:
        account = Account.objects.get(id=account_id, association=user_profile.association)
    except Account.DoesNotExist:
        return Response(
            {'error': 'Account not found or does not belong to your organization'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get opening balance (transactions before start_date)
    opening_debits = VoucherDetail.objects.filter(
        account=account,
        voucher__date__lt=start_date,
        voucher__association=user_profile.association
    ).aggregate(total=Sum('debit'))['total'] or 0
    
    opening_credits = VoucherDetail.objects.filter(
        account=account,
        voucher__date__lt=start_date,
        voucher__association=user_profile.association
    ).aggregate(total=Sum('credit'))['total'] or 0
    
    opening_balance = opening_debits - opening_credits
    
    # Get transactions within date range
    transactions = VoucherDetail.objects.filter(
        account=account,
        voucher__date__gte=start_date,
        voucher__date__lte=end_date,
        voucher__association=user_profile.association
    ).select_related('voucher').order_by('voucher__date', 'id')
    
    # Build transaction list with running balance
    transaction_data = []
    running_balance = opening_balance
    
    for transaction in transactions:
        # Update running balance
        running_balance += transaction.debit - transaction.credit
        
        transaction_data.append({
            'id': transaction.id,
            'date': transaction.voucher.date,
            'voucher_number': transaction.voucher.voucher_number,
            'description': transaction.voucher.description,
            'transaction_description': transaction.description,
            'debit': float(transaction.debit),
            'credit': float(transaction.credit),
            'running_balance': float(running_balance),
        })
    
    # Calculate period totals
    period_debits = sum(t['debit'] for t in transaction_data)
    period_credits = sum(t['credit'] for t in transaction_data)
    closing_balance = opening_balance + period_debits - period_credits
    
    return Response({
        'account': {
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'account_type': account.account_type,
        },
        'date_range': {
            'start_date': start_date,
            'end_date': end_date,
        },
        'opening_balance': float(opening_balance),
        'transactions': transaction_data,
        'period_totals': {
            'debits': float(period_debits),
            'credits': float(period_credits),
        },
        'closing_balance': float(closing_balance),
    })
