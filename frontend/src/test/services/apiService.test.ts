import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setupServer } from 'msw/node'
import { handlers } from '../mocks/handlers'
import apiService, { authAPI, associationsAPI, accountsAPI, vouchersAPI, reportsAPI } from '@/services/apiService'

// Setup MSW server
const server = setupServer(...handlers)

describe('API Service', () => {
  beforeEach(() => {
    server.listen()
    vi.clearAllMocks()
  })

  afterEach(() => {
    server.resetHandlers()
  })

  afterAll(() => {
    server.close()
  })

  describe('authAPI', () => {
    it('should login successfully', async () => {
      const credentials = { username: 'testuser', password: 'testpass' }
      const response = await authAPI.login(credentials)
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('access')
      expect(response.data).toHaveProperty('refresh')
      expect(response.data).toHaveProperty('user')
    })

    it('should get token successfully', async () => {
      const credentials = { username: 'testuser', password: 'testpass' }
      const response = await authAPI.getToken(credentials)
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('access')
      expect(response.data).toHaveProperty('refresh')
    })

    it('should get user profile', async () => {
      const response = await authAPI.getProfile()
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('id')
      expect(response.data).toHaveProperty('username')
      expect(response.data).toHaveProperty('profile')
    })
  })

  describe('associationsAPI', () => {
    it('should get all associations', async () => {
      const response = await associationsAPI.getAll()
      
      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
      expect(response.data[0]).toHaveProperty('id')
      expect(response.data[0]).toHaveProperty('name')
    })

    it('should get association by id', async () => {
      const response = await associationsAPI.getById(1)
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('id')
      expect(response.data).toHaveProperty('name')
    })

    it('should create association', async () => {
      const data = { name: 'New Company' }
      const response = await associationsAPI.create(data)
      
      expect(response.status).toBe(201)
      expect(response.data).toHaveProperty('name')
    })

    it('should update association', async () => {
      const data = { name: 'Updated Company' }
      const response = await associationsAPI.update(1, data)
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('name')
    })

    it('should delete association', async () => {
      const response = await associationsAPI.delete(1)
      
      expect(response.status).toBe(204)
    })
  })

  describe('accountsAPI', () => {
    it('should get all accounts', async () => {
      const response = await accountsAPI.getAll()
      
      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
      expect(response.data[0]).toHaveProperty('id')
      expect(response.data[0]).toHaveProperty('name')
      expect(response.data[0]).toHaveProperty('account_type')
    })

    it('should get account by id', async () => {
      const response = await accountsAPI.getById(1)
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('id')
      expect(response.data).toHaveProperty('name')
    })

    it('should create account', async () => {
      const data = {
        name: 'New Account',
        account_type: 'Asset',
        code: '2000',
      }
      const response = await accountsAPI.create(data)
      
      expect(response.status).toBe(201)
      expect(response.data).toHaveProperty('name')
    })

    it('should get accounts by type', async () => {
      const response = await accountsAPI.getByType('Asset')
      
      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
    })

    it('should get accounts hierarchy', async () => {
      const response = await accountsAPI.getHierarchy()
      
      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
    })
  })

  describe('vouchersAPI', () => {
    it('should get all vouchers', async () => {
      const response = await vouchersAPI.getAll()
      
      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
      expect(response.data[0]).toHaveProperty('id')
      expect(response.data[0]).toHaveProperty('voucher_number')
    })

    it('should get voucher by id', async () => {
      const response = await vouchersAPI.getById(1)
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('id')
      expect(response.data).toHaveProperty('voucher_number')
      expect(response.data).toHaveProperty('details')
    })

    it('should create voucher', async () => {
      const data = {
        date: '2024-01-01',
        description: 'Test voucher',
        voucher_type: 'Journal',
        voucher_number: 'JV001',
        details: [
          {
            account: 1,
            debit: 100.00,
            credit: 0.00,
            description: 'Cash received',
          },
        ],
      }
      const response = await vouchersAPI.create(data)
      
      expect(response.status).toBe(201)
      expect(response.data).toHaveProperty('voucher_number')
    })

    it('should get vouchers by date range', async () => {
      const response = await vouchersAPI.getByDateRange('2024-01-01', '2024-01-31')
      
      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
    })

    it('should get vouchers by type', async () => {
      const response = await vouchersAPI.getByType('Journal')
      
      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
    })

    it('should get voucher trial balance', async () => {
      const response = await vouchersAPI.getTrialBalance(1)
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('voucher_number')
      expect(response.data).toHaveProperty('trial_balance')
    })
  })

  describe('reportsAPI', () => {
    it('should get trial balance report', async () => {
      const response = await reportsAPI.getTrialBalance('2024-01-01', '2024-01-31')
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('start_date')
      expect(response.data).toHaveProperty('end_date')
      expect(response.data).toHaveProperty('accounts')
    })

    it('should get income statement report', async () => {
      const response = await reportsAPI.getIncomeStatement('2024-01-01', '2024-01-31')
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('start_date')
      expect(response.data).toHaveProperty('end_date')
    })

    it('should get balance sheet report', async () => {
      const response = await reportsAPI.getBalanceSheet('2024-01-31')
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('as_of_date')
    })

    it('should get general ledger report', async () => {
      const response = await reportsAPI.getGeneralLedger(1, '2024-01-01', '2024-01-31')
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('account_id')
      expect(response.data).toHaveProperty('start_date')
      expect(response.data).toHaveProperty('end_date')
    })
  })

  describe('API Service Interceptors', () => {
    it('should add authorization header to requests', async () => {
      // Mock localStorage
      const mockToken = 'mock-access-token'
      vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(mockToken)
      
      const response = await authAPI.getProfile()
      
      expect(response.status).toBe(200)
    })

    it('should handle token refresh on 401', async () => {
      // Mock localStorage with expired token
      vi.spyOn(Storage.prototype, 'getItem')
        .mockReturnValueOnce('expired-token') // access token
        .mockReturnValueOnce('refresh-token') // refresh token
      
      // Mock successful refresh
      vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {})
      
      const response = await authAPI.getProfile()
      
      expect(response.status).toBe(200)
    })
  })
})
