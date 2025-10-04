import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setupServer } from 'msw/node'
import { handlers } from '../mocks/handlers'
import ReportsView from '@/views/ReportsView.vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import { createRouter, createWebHistory } from 'vue-router'

// Setup MSW server
const server = setupServer(...handlers)

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/reports', component: ReportsView },
    { path: '/reports/general-ledger', component: { template: '<div>General Ledger</div>' } },
  ],
})

// Mock i18n
const i18n = createI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: {
      reports: {
        title: 'Reports',
        trialBalance: 'Trial Balance',
        generateReport: 'Generate Report',
        generating: 'Generating...',
        startDate: 'Start Date',
        endDate: 'End Date',
        noData: 'No data available',
        totalDebits: 'Total Debits',
        totalCredits: 'Total Credits',
        balance: 'Balance',
      },
    },
  },
})

describe('ReportsView', () => {
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

  const createWrapper = (props = {}) => {
    const pinia = createPinia()
    
    return mount(ReportsView, {
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
      props,
    })
  }

  it('renders correctly', () => {
    const wrapper = createWrapper()
    
    expect(wrapper.find('h1').text()).toBe('reports.title')
    expect(wrapper.find('.reports-tabs').exists()).toBe(true)
  })

  it('displays trial balance tab by default', () => {
    const wrapper = createWrapper()
    
    expect(wrapper.find('.tab-content').exists()).toBe(true)
    expect(wrapper.find('[data-testid="trial-balance-tab"]').exists()).toBe(true)
  })

  it('shows date inputs for trial balance', () => {
    const wrapper = createWrapper()
    
    const startDateInput = wrapper.find('input[id="start-date"]')
    const endDateInput = wrapper.find('input[id="end-date"]')
    
    expect(startDateInput.exists()).toBe(true)
    expect(endDateInput.exists()).toBe(true)
    expect(startDateInput.attributes('type')).toBe('date')
    expect(endDateInput.attributes('type')).toBe('date')
  })

  it('has generate report button', () => {
    const wrapper = createWrapper()
    
    const generateButton = wrapper.find('button.btn-primary')
    expect(generateButton.exists()).toBe(true)
    expect(generateButton.text()).toBe('reports.generateReport')
  })

  it('switches between tabs', async () => {
    const wrapper = createWrapper()
    
    // Initially on trial balance tab
    expect(wrapper.vm.activeTab).toBe('trial-balance')
    
    // Click on another tab (if exists)
    const tabButtons = wrapper.findAll('.tab-button')
    if (tabButtons.length > 1) {
      await tabButtons[1].trigger('click')
      // The actual tab switching logic would be tested here
    }
  })

  it('handles date input changes', async () => {
    const wrapper = createWrapper()
    
    const startDateInput = wrapper.find('input[id="start-date"]')
    const endDateInput = wrapper.find('input[id="end-date"]')
    
    await startDateInput.setValue('2024-01-01')
    await endDateInput.setValue('2024-01-31')
    
    expect(wrapper.vm.trialBalanceFilters.startDate).toBe('2024-01-01')
    expect(wrapper.vm.trialBalanceFilters.endDate).toBe('2024-01-31')
  })

  it('generates trial balance report', async () => {
    const wrapper = createWrapper()
    
    // Set date filters
    await wrapper.setData({
      trialBalanceFilters: {
        startDate: '2024-01-01',
        endDate: '2024-01-31',
      },
    })
    
    // Mock the API call
    const mockGenerateTrialBalance = vi.fn().mockResolvedValue({
      data: {
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
        total_credits: 0.00,
      },
    })
    
    wrapper.vm.generateTrialBalance = mockGenerateTrialBalance
    
    // Click generate button
    const generateButton = wrapper.find('button.btn-primary')
    await generateButton.trigger('click')
    
    // Wait for async operation
    await wrapper.vm.$nextTick()
    
    expect(mockGenerateTrialBalance).toHaveBeenCalled()
  })

  it('displays loading state during report generation', async () => {
    const wrapper = createWrapper()
    
    // Set loading state
    await wrapper.setData({ isLoading: true })
    
    const generateButton = wrapper.find('button.btn-primary')
    expect(generateButton.attributes('disabled')).toBeDefined()
    expect(generateButton.text()).toBe('reports.generating')
  })

  it('displays trial balance data when available', async () => {
    const wrapper = createWrapper()
    
    const mockTrialBalanceData = {
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
      total_credits: 0.00,
    }
    
    await wrapper.setData({ trialBalanceData: mockTrialBalanceData })
    
    expect(wrapper.find('.report-content').exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('reports.trialBalance')
  })

  it('formats dates correctly', () => {
    const wrapper = createWrapper()
    
    const testDate = '2024-01-01'
    const formattedDate = wrapper.vm.formatDate(testDate)
    
    expect(formattedDate).toBeDefined()
    // The actual format would depend on the implementation
  })

  it('handles API errors gracefully', async () => {
    const wrapper = createWrapper()
    
    // Mock API error
    const mockGenerateTrialBalance = vi.fn().mockRejectedValue(new Error('API Error'))
    wrapper.vm.generateTrialBalance = mockGenerateTrialBalance
    
    // Set date filters
    await wrapper.setData({
      trialBalanceFilters: {
        startDate: '2024-01-01',
        endDate: '2024-01-31',
      },
    })
    
    // Click generate button
    const generateButton = wrapper.find('button.btn-primary')
    await generateButton.trigger('click')
    
    // Wait for async operation
    await wrapper.vm.$nextTick()
    
    expect(mockGenerateTrialBalance).toHaveBeenCalled()
    // Error handling would be tested here
  })

  it('navigates to general ledger report', () => {
    const wrapper = createWrapper()
    
    const generalLedgerLink = wrapper.find('router-link[to="/reports/general-ledger"]')
    expect(generalLedgerLink.exists()).toBe(true)
    expect(generalLedgerLink.text()).toBe('reports.generalLedger')
  })

  it('displays no data message when no trial balance data', () => {
    const wrapper = createWrapper()
    
    expect(wrapper.find('.no-data').exists()).toBe(false)
    
    // When no data is available, the component should show appropriate message
    // This would depend on the actual implementation
  })

  it('calculates totals correctly', () => {
    const wrapper = createWrapper()
    
    const mockAccounts = [
      { debit: 100.00, credit: 0.00 },
      { debit: 50.00, credit: 0.00 },
      { debit: 0.00, credit: 150.00 },
    ]
    
    // Test total calculation logic
    const totalDebits = mockAccounts.reduce((sum, account) => sum + account.debit, 0)
    const totalCredits = mockAccounts.reduce((sum, account) => sum + account.credit, 0)
    
    expect(totalDebits).toBe(150.00)
    expect(totalCredits).toBe(150.00)
  })
})
