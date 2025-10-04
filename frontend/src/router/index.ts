import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/select-association',
      name: 'select-association',
      component: () => import('../views/AssociationSelectionView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/chart-of-accounts',
      name: 'chart-of-accounts',
      component: () => import('../views/ChartOfAccountsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/vouchers',
      name: 'vouchers',
      component: () => import('../views/VouchersView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/vouchers/create',
      name: 'voucher-create',
      component: () => import('../views/VoucherCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/vouchers/:id',
      name: 'voucher-detail',
      component: () => import('../views/VoucherDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/vouchers/:id/edit',
      name: 'voucher-edit',
      component: () => import('../views/VoucherEditView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('../views/ReportsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/reports/general-ledger',
      name: 'general-ledger',
      component: () => import('../views/GeneralLedgerReportView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/default-accounts',
      name: 'default-accounts',
      component: () => import('../views/DefaultAccountsView.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Load user from storage if not already loaded
  if (!authStore.user && !authStore.token) {
    authStore.loadUserFromStorage()
  }
  
  console.log('Router guard:', { 
    path: to.path, 
    requiresAuth: to.meta.requiresAuth, 
    isAuthenticated: authStore.isAuthenticated,
    hasUser: !!authStore.user,
    hasToken: !!authStore.token
  })
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('Redirecting to login - not authenticated')
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    console.log('Redirecting to select-association - already authenticated')
    next('/select-association')
  } else if (to.path === '/' && authStore.isAuthenticated) {
    // Check if user has selected an association
    if (authStore.user && authStore.user.association_id) {
      console.log('User has association, proceeding to home')
      next()
    } else {
      console.log('User needs to select association')
      next('/select-association')
    }
  } else {
    console.log('Proceeding normally')
    next()
  }
})

export default router
