import axios, { type AxiosInstance, type AxiosResponse } from 'axios'

// Create axios instance with base configuration
const apiService: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add JWT token to every request
apiService.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
apiService.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // If token is expired and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
            refresh: refreshToken,
          })

          const { access } = response.data
          localStorage.setItem('access_token', access)
          
          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`
          return apiService(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API methods
export const authAPI = {
  login: (credentials: { username: string; password: string }) => {
    console.log('API Service: Making login request to /auth/login/', credentials)
    return apiService.post('/auth/login/', credentials)
  },
  
  register: (userData: {
    username: string
    email: string
    password: string
    first_name: string
    last_name: string
    association_id: number
  }) =>
    apiService.post('/auth/register/', userData),
  
  getProfile: () =>
    apiService.get('/auth/profile/'),
  
  switchAssociation: (associationId: number) =>
    apiService.post('/auth/switch-association/', { association_id: associationId }),
  
  getToken: (credentials: { username: string; password: string }) =>
    apiService.post('/token/', credentials),
  
  refreshToken: (refresh: string) =>
    apiService.post('/token/refresh/', { refresh }),
}

export const associationsAPI = {
  getAll: () =>
    apiService.get('/associations/all/'),
  
  getById: (id: number) =>
    apiService.get(`/associations/${id}/`),
  
  create: (data: { name: string }) =>
    apiService.post('/associations/', data),
  
  update: (id: number, data: { name: string }) =>
    apiService.put(`/associations/${id}/`, data),
  
  delete: (id: number) =>
    apiService.delete(`/associations/${id}/`),
}

export const accountsAPI = {
  getAll: () =>
    apiService.get('/accounts/'),
  
  getById: (id: number) =>
    apiService.get(`/accounts/${id}/`),
  
  create: (data: {
    name: string
    account_type: string
    parent?: number
    code: string
    is_active?: boolean
  }) =>
    apiService.post('/accounts/', data),
  
  update: (id: number, data: {
    name: string
    account_type: string
    parent?: number
    code: string
    is_active?: boolean
  }) =>
    apiService.put(`/accounts/${id}/`, data),
  
  delete: (id: number) =>
    apiService.delete(`/accounts/${id}/`),
  
  getByType: (type: string) =>
    apiService.get(`/accounts/by_type/?type=${type}`),
  
  getHierarchy: () =>
    apiService.get('/accounts/hierarchy/'),
}

export const vouchersAPI = {
  getAll: () =>
    apiService.get('/vouchers/'),
  
  getById: (id: number) =>
    apiService.get(`/vouchers/${id}/`),
  
  create: (data: {
    date: string
    description: string
    voucher_type: string
    voucher_number: string
    details: Array<{
      account: number
      debit: number
      credit: number
      description?: string
    }>
  }) =>
    apiService.post('/vouchers/', data),
  
  update: (id: number, data: {
    date: string
    description: string
    voucher_type: string
    voucher_number: string
    details: Array<{
      account: number
      debit: number
      credit: number
      description?: string
    }>
  }) =>
    apiService.put(`/vouchers/${id}/`, data),
  
  delete: (id: number) =>
    apiService.delete(`/vouchers/${id}/`),
  
  getByDateRange: (startDate: string, endDate: string) =>
    apiService.get(`/vouchers/by_date_range/?start_date=${startDate}&end_date=${endDate}`),
  
  getByType: (type: string) =>
    apiService.get(`/vouchers/by_type/?type=${type}`),
  
  getTrialBalance: (id: number) =>
    apiService.get(`/vouchers/${id}/trial_balance/`),
  
  getNextVoucherNumber: (type: string) =>
    apiService.get(`/vouchers/next_voucher_number/?type=${type}`),
}

export const voucherDetailsAPI = {
  getAll: () =>
    apiService.get('/voucher-details/'),
  
  getById: (id: number) =>
    apiService.get(`/voucher-details/${id}/`),
  
  create: (data: {
    voucher: number
    account: number
    debit: number
    credit: number
    description?: string
  }) =>
    apiService.post('/voucher-details/', data),
  
  update: (id: number, data: {
    voucher: number
    account: number
    debit: number
    credit: number
    description?: string
  }) =>
    apiService.put(`/voucher-details/${id}/`, data),
  
  delete: (id: number) =>
    apiService.delete(`/voucher-details/${id}/`),
}

export const reportsAPI = {
  getTrialBalance: (startDate: string, endDate: string) =>
    apiService.get(`/reports/trial-balance/?start_date=${startDate}&end_date=${endDate}`),
  
  getIncomeStatement: (startDate: string, endDate: string) =>
    apiService.get(`/reports/income-statement/?start_date=${startDate}&end_date=${endDate}`),
  
  getBalanceSheet: (asOfDate: string) =>
    apiService.get(`/reports/balance-sheet/?as_of_date=${asOfDate}`),
  
  getGeneralLedger: (accountId: number, startDate: string, endDate: string) =>
    apiService.get(`/reports/general-ledger/?account_id=${accountId}&start_date=${startDate}&end_date=${endDate}`),
}

export const defaultAccountTemplatesAPI = {
  getAll: () =>
    apiService.get('/default-account-templates/'),
  
  getById: (id: number) =>
    apiService.get(`/default-account-templates/${id}/`),
  
  create: (data: {
    name: string
    account_type: string
    parent?: number
    code: string
    is_active?: boolean
  }) =>
    apiService.post('/default-account-templates/', data),
  
  update: (id: number, data: {
    name: string
    account_type: string
    parent?: number
    code: string
    is_active?: boolean
  }) =>
    apiService.put(`/default-account-templates/${id}/`, data),
  
  delete: (id: number) =>
    apiService.delete(`/default-account-templates/${id}/`),
  
  applyToAssociation: (associationId: number) =>
    apiService.post('/default-account-templates/apply_to_association/', { association_id: associationId }),
}

export default apiService

