import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import { createRouter, createWebHistory } from 'vue-router'
import { vi } from 'vitest'
import type { App } from 'vue'

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } },
    { path: '/reports', component: { template: '<div>Reports</div>' } },
  ],
})

// Mock i18n
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: {
      reports: {
        title: 'Reports',
        trialBalance: 'Trial Balance',
        generateReport: 'Generate Report',
        startDate: 'Start Date',
        endDate: 'End Date',
      },
    },
  },
})

// Mock API service
export const mockApiService = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}

// Mock localStorage
export const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

// Test utilities
export function createTestWrapper(component: any, options: any = {}): VueWrapper<any> {
  const pinia = createPinia()
  
  const defaultOptions = {
    global: {
      plugins: [pinia, router, i18n],
      stubs: {
        'router-link': true,
        'router-view': true,
      },
      mocks: {
        $t: (key: string) => key,
        $router: router,
        $route: router.currentRoute.value,
      },
    },
  }

  return mount(component, {
    ...defaultOptions,
    ...options,
  })
}

// Mock window.location
export function mockLocation(href: string) {
  Object.defineProperty(window, 'location', {
    value: {
      href,
      assign: vi.fn(),
      replace: vi.fn(),
      reload: vi.fn(),
    },
    writable: true,
  })
}

// Mock console methods
export function mockConsole() {
  vi.spyOn(console, 'log').mockImplementation(() => {})
  vi.spyOn(console, 'warn').mockImplementation(() => {})
  vi.spyOn(console, 'error').mockImplementation(() => {})
}

// Wait for next tick
export function nextTick() {
  return new Promise(resolve => setTimeout(resolve, 0))
}

// Mock API responses
export const mockApiResponses = {
  associations: [
    {
      id: 1,
      name: 'Test Company',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ],
  accounts: [
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
  ],
  vouchers: [
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
  ],
  trialBalance: {
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
    ],
    total_debits: 100.00,
    total_credits: 100.00,
  },
}
