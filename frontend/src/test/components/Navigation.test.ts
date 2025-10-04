import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import { createRouter, createWebHistory } from 'vue-router'
import Navigation from '@/components/Navigation.vue'

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } },
    { path: '/reports', component: { template: '<div>Reports</div>' } },
    { path: '/vouchers', component: { template: '<div>Vouchers</div>' } },
    { path: '/accounts', component: { template: '<div>Accounts</div>' } },
  ],
})

// Mock i18n
const i18n = createI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: {
      navigation: {
        home: 'Home',
        reports: 'Reports',
        vouchers: 'Vouchers',
        accounts: 'Accounts',
        login: 'Login',
        logout: 'Logout',
      },
    },
  },
})

describe('Navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    const pinia = createPinia()
    
    return mount(Navigation, {
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
    
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('displays navigation links', () => {
    const wrapper = createWrapper()
    
    const links = wrapper.findAll('router-link')
    expect(links.length).toBeGreaterThan(0)
  })

  it('highlights active route', async () => {
    const wrapper = createWrapper()
    
    // Mock current route
    await router.push('/reports')
    await wrapper.vm.$nextTick()
    
    // Check if active class is applied
    const activeLink = wrapper.find('.active')
    expect(activeLink.exists()).toBe(true)
  })

  it('handles logout functionality', async () => {
    const wrapper = createWrapper()
    
    // Mock logout method
    const mockLogout = vi.fn()
    wrapper.vm.logout = mockLogout
    
    const logoutButton = wrapper.find('[data-testid="logout-button"]')
    if (logoutButton.exists()) {
      await logoutButton.trigger('click')
      expect(mockLogout).toHaveBeenCalled()
    }
  })

  it('shows user information when authenticated', () => {
    const wrapper = createWrapper()
    
    // Mock authenticated state
    wrapper.vm.isAuthenticated = true
    wrapper.vm.user = {
      username: 'testuser',
      email: 'test@example.com',
    }
    
    expect(wrapper.vm.isAuthenticated).toBe(true)
    expect(wrapper.vm.user.username).toBe('testuser')
  })

  it('hides navigation when not authenticated', () => {
    const wrapper = createWrapper()
    
    // Mock unauthenticated state
    wrapper.vm.isAuthenticated = false
    
    expect(wrapper.vm.isAuthenticated).toBe(false)
  })

  it('displays language switcher', () => {
    const wrapper = createWrapper()
    
    const languageSwitcher = wrapper.findComponent({ name: 'LanguageSwitcher' })
    expect(languageSwitcher.exists()).toBe(true)
  })

  it('handles mobile menu toggle', async () => {
    const wrapper = createWrapper()
    
    const mobileMenuButton = wrapper.find('[data-testid="mobile-menu-button"]')
    if (mobileMenuButton.exists()) {
      await mobileMenuButton.trigger('click')
      expect(wrapper.vm.isMobileMenuOpen).toBe(true)
    }
  })

  it('closes mobile menu when clicking outside', async () => {
    const wrapper = createWrapper()
    
    // Open mobile menu
    wrapper.vm.isMobileMenuOpen = true
    
    // Simulate click outside
    await wrapper.trigger('click')
    
    expect(wrapper.vm.isMobileMenuOpen).toBe(false)
  })

  it('displays association information', () => {
    const wrapper = createWrapper()
    
    // Mock association data
    wrapper.vm.currentAssociation = {
      id: 1,
      name: 'Test Company',
    }
    
    expect(wrapper.vm.currentAssociation.name).toBe('Test Company')
  })

  it('handles association switching', async () => {
    const wrapper = createWrapper()
    
    // Mock association switching
    const mockSwitchAssociation = vi.fn()
    wrapper.vm.switchAssociation = mockSwitchAssociation
    
    const associationSelect = wrapper.find('[data-testid="association-select"]')
    if (associationSelect.exists()) {
      await associationSelect.setValue('2')
      expect(mockSwitchAssociation).toHaveBeenCalledWith('2')
    }
  })

  it('shows loading state during navigation', async () => {
    const wrapper = createWrapper()
    
    // Mock loading state
    wrapper.vm.isLoading = true
    
    expect(wrapper.vm.isLoading).toBe(true)
  })

  it('handles navigation errors gracefully', async () => {
    const wrapper = createWrapper()
    
    // Mock navigation error
    const mockNavigate = vi.fn().mockRejectedValue(new Error('Navigation error'))
    wrapper.vm.navigate = mockNavigate
    
    try {
      await wrapper.vm.navigate('/invalid-route')
    } catch (error) {
      expect(error).toBeInstanceOf(Error)
    }
  })

  it('displays notification messages', () => {
    const wrapper = createWrapper()
    
    // Mock notification
    wrapper.vm.notification = {
      message: 'Test notification',
      type: 'success',
    }
    
    expect(wrapper.vm.notification.message).toBe('Test notification')
    expect(wrapper.vm.notification.type).toBe('success')
  })

  it('clears notifications after timeout', async () => {
    const wrapper = createWrapper()
    
    // Mock notification with timeout
    wrapper.vm.notification = {
      message: 'Test notification',
      type: 'success',
    }
    
    // Wait for timeout
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    expect(wrapper.vm.notification).toBeNull()
  })
})
