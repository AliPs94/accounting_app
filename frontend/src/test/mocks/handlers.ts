import { http, HttpResponse } from 'msw'

// Mock API handlers for testing
export const handlers = [
  // Auth endpoints
  http.post('http://127.0.0.1:8000/api/auth/login/', () => {
    return HttpResponse.json({
      access: 'mock-access-token',
      refresh: 'mock-refresh-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
      },
    })
  }),

  http.post('http://127.0.0.1:8000/api/token/', () => {
    return HttpResponse.json({
      access: 'mock-access-token',
      refresh: 'mock-refresh-token',
    })
  }),

  http.get('http://127.0.0.1:8000/api/auth/profile/', () => {
    return HttpResponse.json({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      profile: {
        id: 1,
        association: 1,
        association_name: 'Test Company',
      },
    })
  }),

  // Associations endpoints
  http.get('http://127.0.0.1:8000/api/associations/all/', () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'Test Company',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ])
  }),

  http.get('http://127.0.0.1:8000/api/associations/', () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'Test Company',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ])
  }),

  // Accounts endpoints
  http.get('http://127.0.0.1:8000/api/accounts/', () => {
    return HttpResponse.json([
      {
        id: 1,
        association: 1,
        association_name: 'Test Company',
        name: 'Cash Account',
        account_type: 'Asset',
        parent: null,
        parent_name: null,
        code: '1000',
        is_active: true,
        sub_accounts_count: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ])
  }),

  http.get('http://127.0.0.1:8000/api/accounts/by_type/', () => {
    return HttpResponse.json([
      {
        id: 1,
        association: 1,
        association_name: 'Test Company',
        name: 'Cash Account',
        account_type: 'Asset',
        parent: null,
        parent_name: null,
        code: '1000',
        is_active: true,
        sub_accounts_count: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ])
  }),

  // Vouchers endpoints
  http.get('http://127.0.0.1:8000/api/vouchers/', () => {
    return HttpResponse.json([
      {
        id: 1,
        association_name: 'Test Company',
        date: '2024-01-01',
        description: 'Test voucher',
        voucher_type: 'Journal',
        voucher_number: 'JV001',
        created_by_username: 'testuser',
        total_debits: 100.00,
        total_credits: 100.00,
        details_count: 2,
        created_at: '2024-01-01T00:00:00Z',
      },
    ])
  }),

  http.get('http://127.0.0.1:8000/api/vouchers/1/', () => {
    return HttpResponse.json({
      id: 1,
      association: 1,
      association_name: 'Test Company',
      date: '2024-01-01',
      description: 'Test voucher',
      voucher_type: 'Journal',
      voucher_number: 'JV001',
      created_by: 1,
      created_by_username: 'testuser',
      details: [
        {
          id: 1,
          account: 1,
          account_name: 'Cash',
          account_code: '1000',
          debit: 100.00,
          credit: 0.00,
          description: 'Cash received',
        },
        {
          id: 2,
          account: 2,
          account_name: 'Revenue',
          account_code: '4000',
          debit: 0.00,
          credit: 100.00,
          description: 'Revenue earned',
        },
      ],
      total_debits: 100.00,
      total_credits: 100.00,
      is_balanced: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    })
  }),

  // Reports endpoints
  http.get('http://127.0.0.1:8000/api/reports/trial-balance/', () => {
    return HttpResponse.json({
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      accounts: [
        {
          account_code: '1000',
          account_name: 'Cash',
          account_type: 'Asset',
          debit: 100.00,
          credit: 0.00,
        },
        {
          account_code: '4000',
          account_name: 'Revenue',
          account_type: 'Revenue',
          debit: 0.00,
          credit: 100.00,
        },
      ],
      total_debits: 100.00,
      total_credits: 100.00,
    })
  }),

  // Error handlers
  http.get('http://127.0.0.1:8000/api/error/', () => {
    return HttpResponse.json(
      { error: 'Test error' },
      { status: 500 }
    )
  }),
]
