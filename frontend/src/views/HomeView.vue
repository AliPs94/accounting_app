<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>{{ $t('dashboard.title') }}</h1>
      <p>{{ $t('dashboard.welcomeBack') }}, {{ authStore.userFullName }}!</p>
    </div>

    <div class="dashboard-grid">
      <div class="dashboard-card">
        <h3>{{ $t('dashboard.quickActions') }}</h3>
        <div class="quick-actions">
          <router-link to="/vouchers/create" class="action-button">
            <span class="action-icon">📝</span>
            <span>{{ $t('dashboard.createVoucher') }}</span>
          </router-link>
          <router-link to="/chart-of-accounts" class="action-button">
            <span class="action-icon">📊</span>
            <span>{{ $t('dashboard.chartOfAccounts') }}</span>
          </router-link>
          <router-link to="/reports" class="action-button">
            <span class="action-icon">📈</span>
            <span>{{ $t('dashboard.financialReports') }}</span>
          </router-link>
        </div>
      </div>

      <div class="dashboard-card">
        <h3>{{ $t('dashboard.recentActivity') }}</h3>
        <div v-if="recentVouchers.length === 0" class="empty-state">
          <p>{{ $t('dashboard.noRecentVouchers') }}</p>
          <router-link to="/vouchers/create" class="btn-primary">{{ $t('dashboard.createFirstVoucher') }}</router-link>
        </div>
        <div v-else class="recent-list">
          <div v-for="voucher in recentVouchers" :key="voucher.id" class="recent-item">
            <div class="recent-info">
              <span class="voucher-number">{{ voucher.voucher_number }}</span>
              <span class="voucher-description">{{ voucher.description }}</span>
            </div>
            <div class="recent-meta">
              <span class="voucher-date">{{ formatDate(voucher.date) }}</span>
              <span class="voucher-amount">${{ voucher.total_debits.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-card">
        <h3>{{ $t('dashboard.accountSummary') }}</h3>
        <div v-if="accountSummary.length === 0" class="empty-state">
          <p>{{ $t('dashboard.noAccountsFound') }}</p>
          <router-link to="/chart-of-accounts" class="btn-primary">{{ $t('dashboard.setUpAccounts') }}</router-link>
        </div>
        <div v-else class="summary-list">
          <div v-for="summary in accountSummary" :key="summary.type" class="summary-item">
            <span class="summary-type">{{ summary.type }}</span>
            <span class="summary-count">{{ summary.count }} {{ $t('dashboard.accounts') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { vouchersAPI, accountsAPI } from '@/services/apiService'

const authStore = useAuthStore()
const recentVouchers = ref([])
const accountSummary = ref([])

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const loadRecentVouchers = async () => {
  try {
    const response = await vouchersAPI.getAll()
    recentVouchers.value = response.data.results.slice(0, 5) // Get latest 5
  } catch (error) {
    console.error('Failed to load recent vouchers:', error)
  }
}

const loadAccountSummary = async () => {
  try {
    const response = await accountsAPI.getAll()
    const accounts = response.data.results
    
    const summary = [
      { type: 'Assets', count: accounts.filter(a => a.account_type === 'Asset').length },
      { type: 'Liabilities', count: accounts.filter(a => a.account_type === 'Liability').length },
      { type: 'Equity', count: accounts.filter(a => a.account_type === 'Equity').length },
      { type: 'Revenue', count: accounts.filter(a => a.account_type === 'Revenue').length },
      { type: 'Expenses', count: accounts.filter(a => a.account_type === 'Expense').length },
    ]
    
    accountSummary.value = summary.filter(s => s.count > 0)
  } catch (error) {
    console.error('Failed to load account summary:', error)
  }
}

onMounted(() => {
  loadRecentVouchers()
  loadAccountSummary()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: #333;
}

.page-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.dashboard-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  text-decoration: none;
  color: #333;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: #e9ecef;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.action-icon {
  font-size: 20px;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
}

.empty-state p {
  margin: 0 0 15px 0;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #007bff;
}

.recent-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.voucher-number {
  font-weight: 600;
  color: #333;
}

.voucher-description {
  font-size: 14px;
  color: #666;
}

.recent-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.voucher-date {
  font-size: 12px;
  color: #999;
}

.voucher-amount {
  font-weight: 600;
  color: #28a745;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.summary-type {
  font-weight: 500;
  color: #333;
}

.summary-count {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .recent-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .recent-meta {
    align-items: flex-start;
  }
}
</style>
