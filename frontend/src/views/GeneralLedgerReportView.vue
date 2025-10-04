<template>
  <div class="general-ledger-report">
    <div class="page-header">
      <h1>{{ $t('reports.generalLedger') }}</h1>
    </div>

    <div class="report-controls">
      <div class="controls-grid">
        <div class="form-group">
          <label for="account">{{ $t('reports.account') }} *</label>
          <select id="account" v-model="selectedAccountId" required>
            <option value="">{{ $t('reports.selectAccount') }}</option>
            <option v-for="account in accounts" :key="account.id" :value="account.id">
              {{ account.code }} - {{ account.name }} ({{ account.account_type }})
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="start-date">{{ $t('reports.startDate') }} *</label>
          <input
            id="start-date"
            v-model="filters.startDate"
            type="date"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="end-date">{{ $t('reports.endDate') }} *</label>
          <input
            id="end-date"
            v-model="filters.endDate"
            type="date"
            required
          />
        </div>
        
        <div class="form-group">
          <button @click="generateReport" class="btn-primary" :disabled="!canGenerate">
            {{ isLoading ? $t('reports.generating') : $t('reports.generateReport') }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="reportData" class="report-content">
      <div class="report-header">
        <h2>{{ $t('reports.generalLedger') }}</h2>
        <div class="account-info">
          <h3>{{ reportData.account.code }} - {{ reportData.account.name }}</h3>
          <p>{{ reportData.account.account_type }} {{ $t('reports.account') }}</p>
        </div>
        <div class="date-range">
          <p>{{ formatDate(reportData.date_range.start_date) }} {{ $t('reports.asOf') }} {{ formatDate(reportData.date_range.end_date) }}</p>
        </div>
      </div>

      <div class="balance-summary">
        <div class="balance-item">
          <span class="balance-label">{{ $t('reports.openingBalance') }}:</span>
          <span class="balance-amount">{{ formatCurrency(reportData.opening_balance) }}</span>
        </div>
        <div class="balance-item">
          <span class="balance-label">{{ $t('reports.periodDebits') }}:</span>
          <span class="balance-amount">{{ formatCurrency(reportData.period_totals.debits) }}</span>
        </div>
        <div class="balance-item">
          <span class="balance-label">{{ $t('reports.periodCredits') }}:</span>
          <span class="balance-amount">{{ formatCurrency(reportData.period_totals.credits) }}</span>
        </div>
        <div class="balance-item total">
          <span class="balance-label">{{ $t('reports.closingBalance') }}:</span>
          <span class="balance-amount">{{ formatCurrency(reportData.closing_balance) }}</span>
        </div>
      </div>

      <div v-if="reportData.transactions.length === 0" class="empty-state">
        <p>{{ $t('reports.noTransactions') }}</p>
      </div>

      <div v-else class="transactions-table">
        <table>
          <thead>
            <tr>
              <th>{{ $t('reports.date') }}</th>
              <th>{{ $t('reports.voucherNumber') }}</th>
              <th>{{ $t('reports.description') }}</th>
              <th>{{ $t('reports.debit') }}</th>
              <th>{{ $t('reports.credit') }}</th>
              <th>{{ $t('reports.runningBalance') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in reportData.transactions" :key="transaction.id">
              <td>{{ formatDate(transaction.date) }}</td>
              <td>{{ transaction.voucher_number }}</td>
              <td>
                <div class="description">
                  <div class="voucher-desc">{{ transaction.description }}</div>
                  <div v-if="transaction.transaction_description" class="transaction-desc">
                    {{ transaction.transaction_description }}
                  </div>
                </div>
              </td>
              <td class="amount">
                <span v-if="transaction.debit > 0">{{ formatCurrency(transaction.debit) }}</span>
                <span v-else>-</span>
              </td>
              <td class="amount">
                <span v-if="transaction.credit > 0">{{ formatCurrency(transaction.credit) }}</span>
                <span v-else>-</span>
              </td>
              <td class="amount running-balance" :class="{ 'positive': transaction.running_balance >= 0, 'negative': transaction.running_balance < 0 }">
                {{ formatCurrency(transaction.running_balance) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { accountsAPI, reportsAPI } from '@/services/apiService'
import type { Account } from '@/types/accounting'

// State
const accounts = ref<Account[]>([])
const selectedAccountId = ref<number | ''>('')
const isLoading = ref(false)
const error = ref('')
const reportData = ref(null)

const filters = reactive({
  startDate: '',
  endDate: ''
})

// Computed
const canGenerate = computed(() => {
  return selectedAccountId.value && filters.startDate && filters.endDate && !isLoading.value
})

// Methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const loadAccounts = async () => {
  try {
    const response = await accountsAPI.getAll()
    accounts.value = response.data.results.filter(account => account.is_active)
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load accounts'
  }
}

const generateReport = async () => {
  if (!canGenerate.value) return

  isLoading.value = true
  error.value = ''

  try {
    const response = await reportsAPI.getGeneralLedger(
      Number(selectedAccountId.value),
      filters.startDate,
      filters.endDate
    )
    reportData.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to generate general ledger report'
  } finally {
    isLoading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAccounts()
  
  // Set default dates to current month
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  
  filters.startDate = firstDay.toISOString().split('T')[0]
  filters.endDate = lastDay.toISOString().split('T')[0]
})
</script>

<style scoped>
.general-ledger-report {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: #333;
}

.report-controls {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.controls-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 20px;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.report-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.report-header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 20px;
}

.report-header h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.account-info h3 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 18px;
}

.account-info p {
  margin: 0;
  color: #666;
}

.date-range p {
  margin: 10px 0 0 0;
  color: #666;
  font-weight: 500;
}

.balance-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.balance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.balance-item.total {
  background: #e3f2fd;
  border-color: #007bff;
  font-weight: 600;
}

.balance-label {
  color: #333;
  font-weight: 500;
}

.balance-amount {
  font-weight: 600;
  color: #333;
  font-family: monospace;
}

.transactions-table {
  overflow-x: auto;
}

.transactions-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.transactions-table th,
.transactions-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.transactions-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
  position: sticky;
  top: 0;
}

.transactions-table tr:hover {
  background: #f8f9fa;
}

.transactions-table .amount {
  text-align: right;
  font-family: monospace;
  font-weight: 500;
}

.running-balance.positive {
  color: #28a745;
}

.running-balance.negative {
  color: #dc3545;
}

.description {
  max-width: 300px;
}

.voucher-desc {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.transaction-desc {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f8f9fa;
  border-radius: 4px;
  border: 2px dashed #ddd;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .controls-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .balance-summary {
    grid-template-columns: 1fr;
  }
  
  .transactions-table {
    font-size: 14px;
  }
  
  .transactions-table th,
  .transactions-table td {
    padding: 8px;
  }
  
  .description {
    max-width: 200px;
  }
}
</style>
