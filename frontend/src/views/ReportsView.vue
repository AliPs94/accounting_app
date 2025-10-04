<template>
  <div class="reports">
    <div class="page-header">
      <h1>{{ $t('reports.title') }}</h1>
    </div>

    <div class="reports-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
      >
        {{ tab.name }}
      </button>
      <router-link to="/reports/general-ledger" class="tab-button">
        {{ $t('reports.generalLedger') }}
      </router-link>
    </div>

    <!-- Trial Balance Tab -->
    <div v-if="activeTab === 'trial-balance'" class="tab-content">
      <div class="report-controls">
        <div class="date-inputs">
          <div class="form-group">
            <label for="start-date">{{ $t('reports.startDate') }}</label>
            <input
              id="start-date"
              v-model="trialBalanceFilters.startDate"
              type="date"
            />
          </div>
          <div class="form-group">
            <label for="end-date">{{ $t('reports.endDate') }}</label>
            <input
              id="end-date"
              v-model="trialBalanceFilters.endDate"
              type="date"
            />
          </div>
          <button @click="generateTrialBalance" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? $t('reports.generating') : $t('reports.generateReport') }}
          </button>
        </div>
      </div>

      <div v-if="trialBalanceData" class="report-content">
        <div class="report-header">
          <h2>{{ $t('reports.trialBalance') }}</h2>
          <p>{{ formatDate(trialBalanceData.start_date) }} to {{ formatDate(trialBalanceData.end_date) }}</p>
        </div>

        <div class="report-table">
          <table>
            <thead>
              <tr>
                <th>{{ $t('reports.accountCode') }}</th>
                <th>{{ $t('reports.accountName') }}</th>
                <th>{{ $t('reports.type') }}</th>
                <th>{{ $t('reports.openingBalance') }}</th>
                <th>{{ $t('reports.periodDebits') }}</th>
                <th>{{ $t('reports.periodCredits') }}</th>
                <th>{{ $t('reports.closingBalance') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in trialBalanceData.trial_balance" :key="item.account_id">
                <td>{{ item.account_code }}</td>
                <td>{{ item.account_name }}</td>
                <td>
                  <span :class="`account-type-badge ${item.account_type.toLowerCase()}`">
                    {{ item.account_type }}
                  </span>
                </td>
                <td class="amount">{{ formatCurrency(item.opening_balance) }}</td>
                <td class="amount">{{ formatCurrency(item.period_debits) }}</td>
                <td class="amount">{{ formatCurrency(item.period_credits) }}</td>
                <td class="amount">{{ formatCurrency(item.closing_balance) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="totals-row">
                <td colspan="3"><strong>{{ $t('reports.totals') }}</strong></td>
                <td class="amount">{{ formatCurrency(trialBalanceData.totals.opening_debits - trialBalanceData.totals.opening_credits) }}</td>
                <td class="amount">{{ formatCurrency(trialBalanceData.totals.period_debits) }}</td>
                <td class="amount">{{ formatCurrency(trialBalanceData.totals.period_credits) }}</td>
                <td class="amount">{{ formatCurrency(trialBalanceData.totals.closing_debits - trialBalanceData.totals.closing_credits) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>

    <!-- Income Statement Tab -->
    <div v-if="activeTab === 'income-statement'" class="tab-content">
      <div class="report-controls">
        <div class="date-inputs">
          <div class="form-group">
            <label for="is-start-date">{{ $t('reports.startDate') }}</label>
            <input
              id="is-start-date"
              v-model="incomeStatementFilters.startDate"
              type="date"
            />
          </div>
          <div class="form-group">
            <label for="is-end-date">{{ $t('reports.endDate') }}</label>
            <input
              id="is-end-date"
              v-model="incomeStatementFilters.endDate"
              type="date"
            />
          </div>
          <button @click="generateIncomeStatement" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? $t('reports.generating') : $t('reports.generateReport') }}
          </button>
        </div>
      </div>

      <div v-if="incomeStatementData" class="report-content">
        <div class="report-header">
          <h2>{{ $t('reports.incomeStatement') }}</h2>
          <p>{{ formatDate(incomeStatementData.start_date) }} to {{ formatDate(incomeStatementData.end_date) }}</p>
        </div>

        <div class="income-statement">
          <!-- Revenue Section -->
          <div class="statement-section">
            <h3>{{ $t('reports.revenue') }}</h3>
            <div v-for="item in incomeStatementData.revenue.items" :key="item.account_code" class="statement-item">
              <span>{{ item.account_code }} - {{ item.account_name }}</span>
              <span class="amount">{{ formatCurrency(item.amount) }}</span>
            </div>
            <div class="statement-total">
              <span><strong>{{ $t('reports.totalRevenue') }}</strong></span>
              <span class="amount"><strong>{{ formatCurrency(incomeStatementData.revenue.total) }}</strong></span>
            </div>
          </div>

          <!-- Expenses Section -->
          <div class="statement-section">
            <h3>{{ $t('reports.expenses') }}</h3>
            <div v-for="item in incomeStatementData.expenses.items" :key="item.account_code" class="statement-item">
              <span>{{ item.account_code }} - {{ item.account_name }}</span>
              <span class="amount">{{ formatCurrency(item.amount) }}</span>
            </div>
            <div class="statement-total">
              <span><strong>{{ $t('reports.totalExpenses') }}</strong></span>
              <span class="amount"><strong>{{ formatCurrency(incomeStatementData.expenses.total) }}</strong></span>
            </div>
          </div>

          <!-- Net Income Section -->
          <div class="statement-section net-income">
            <div class="statement-total">
              <span><strong>{{ incomeStatementData.is_profit ? $t('reports.netIncome') : $t('reports.netLoss') }}</strong></span>
              <span class="amount" :class="{ 'profit': incomeStatementData.is_profit, 'loss': !incomeStatementData.is_profit }">
                <strong>{{ formatCurrency(Math.abs(incomeStatementData.net_income)) }}</strong>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Balance Sheet Tab -->
    <div v-if="activeTab === 'balance-sheet'" class="tab-content">
      <div class="report-controls">
        <div class="date-inputs">
          <div class="form-group">
            <label for="bs-date">{{ $t('reports.asOfDate') }}</label>
            <input
              id="bs-date"
              v-model="balanceSheetFilters.asOfDate"
              type="date"
            />
          </div>
          <button @click="generateBalanceSheet" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? $t('reports.generating') : $t('reports.generateReport') }}
          </button>
        </div>
      </div>

      <div v-if="balanceSheetData" class="report-content">
        <div class="report-header">
          <h2>{{ $t('reports.balanceSheet') }}</h2>
          <p>{{ $t('reports.asOf') }} {{ formatDate(balanceSheetData.as_of_date) }}</p>
        </div>

        <div class="balance-sheet">
          <div class="balance-sheet-columns">
            <!-- Assets Column -->
            <div class="bs-column">
              <h3>{{ $t('reports.assets') }}</h3>
              <div v-for="item in balanceSheetData.assets.items" :key="item.account_code" class="bs-item">
                <span>{{ item.account_code }} - {{ item.account_name }}</span>
                <span class="amount">{{ formatCurrency(item.balance) }}</span>
              </div>
              <div class="bs-total">
                <span><strong>{{ $t('reports.totalAssets') }}</strong></span>
                <span class="amount"><strong>{{ formatCurrency(balanceSheetData.assets.total) }}</strong></span>
              </div>
            </div>

            <!-- Liabilities & Equity Column -->
            <div class="bs-column">
              <h3>{{ $t('reports.liabilities') }}</h3>
              <div v-for="item in balanceSheetData.liabilities.items" :key="item.account_code" class="bs-item">
                <span>{{ item.account_code }} - {{ item.account_name }}</span>
                <span class="amount">{{ formatCurrency(item.balance) }}</span>
              </div>
              <div class="bs-total">
                <span><strong>{{ $t('reports.totalLiabilities') }}</strong></span>
                <span class="amount"><strong>{{ formatCurrency(balanceSheetData.liabilities.total) }}</strong></span>
              </div>

              <h3>{{ $t('reports.equity') }}</h3>
              <div v-for="item in balanceSheetData.equity.items" :key="item.account_code" class="bs-item">
                <span>{{ item.account_code }} - {{ item.account_name }}</span>
                <span class="amount">{{ formatCurrency(item.balance) }}</span>
              </div>
              <div class="bs-total">
                <span><strong>{{ $t('reports.totalEquity') }}</strong></span>
                <span class="amount"><strong>{{ formatCurrency(balanceSheetData.equity.total) }}</strong></span>
              </div>

              <div class="bs-total final-total">
                <span><strong>{{ $t('reports.totalLiabilitiesAndEquity') }}</strong></span>
                <span class="amount"><strong>{{ formatCurrency(balanceSheetData.total_equity_and_liabilities) }}</strong></span>
              </div>
            </div>
          </div>

          <div v-if="!balanceSheetData.is_balanced" class="balance-warning">
            ⚠️ {{ $t('reports.balanceSheetNotBalanced') }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { reportsAPI } from '@/services/apiService'

const { t } = useI18n()

// State
const activeTab = ref('trial-balance')
const isLoading = ref(false)
const error = ref('')

const tabs = [
  { id: 'trial-balance', name: t('reports.trialBalance') },
  { id: 'income-statement', name: t('reports.incomeStatement') },
  { id: 'balance-sheet', name: t('reports.balanceSheet') }
]

// Report data
const trialBalanceData = ref(null)
const incomeStatementData = ref(null)
const balanceSheetData = ref(null)

// Filters
const trialBalanceFilters = reactive({
  startDate: '',
  endDate: ''
})

const incomeStatementFilters = reactive({
  startDate: '',
  endDate: ''
})

const balanceSheetFilters = reactive({
  asOfDate: ''
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

const generateTrialBalance = async () => {
  if (!trialBalanceFilters.startDate || !trialBalanceFilters.endDate) {
    error.value = t('reports.selectBothDates')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await reportsAPI.getTrialBalance(
      trialBalanceFilters.startDate,
      trialBalanceFilters.endDate
    )
    trialBalanceData.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.error || t('reports.failedToGenerateTrialBalance')
  } finally {
    isLoading.value = false
  }
}

const generateIncomeStatement = async () => {
  if (!incomeStatementFilters.startDate || !incomeStatementFilters.endDate) {
    error.value = t('reports.selectBothDates')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await reportsAPI.getIncomeStatement(
      incomeStatementFilters.startDate,
      incomeStatementFilters.endDate
    )
    incomeStatementData.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.error || t('reports.failedToGenerateIncomeStatement')
  } finally {
    isLoading.value = false
  }
}

const generateBalanceSheet = async () => {
  if (!balanceSheetFilters.asOfDate) {
    error.value = t('reports.selectAsOfDate')
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const response = await reportsAPI.getBalanceSheet(balanceSheetFilters.asOfDate)
    balanceSheetData.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.error || t('reports.failedToGenerateBalanceSheet')
  } finally {
    isLoading.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Set default dates to current month
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  
  trialBalanceFilters.startDate = firstDay.toISOString().split('T')[0]
  trialBalanceFilters.endDate = lastDay.toISOString().split('T')[0]
  
  incomeStatementFilters.startDate = firstDay.toISOString().split('T')[0]
  incomeStatementFilters.endDate = lastDay.toISOString().split('T')[0]
  
  balanceSheetFilters.asOfDate = today.toISOString().split('T')[0]
})
</script>

<style scoped>
.reports {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header h1 {
  margin: 0 0 30px 0;
  color: #333;
}

.reports-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-button:hover {
  color: #333;
}

.tab-button.active {
  color: #007bff;
  border-bottom-color: #007bff;
}

.tab-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.report-controls {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.date-inputs {
  display: flex;
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

.form-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.report-header {
  text-align: center;
  margin-bottom: 30px;
}

.report-header h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.report-header p {
  margin: 0;
  color: #666;
}

.report-table {
  overflow-x: auto;
}

.report-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.report-table th,
.report-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.report-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.report-table .amount {
  text-align: right;
  font-family: monospace;
}

.totals-row {
  background: #f8f9fa;
  font-weight: 600;
}

.account-type-badge {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.account-type-badge.asset { background: #d4edda; color: #155724; }
.account-type-badge.liability { background: #f8d7da; color: #721c24; }
.account-type-badge.equity { background: #d1ecf1; color: #0c5460; }
.account-type-badge.revenue { background: #d4edda; color: #155724; }
.account-type-badge.expense { background: #fff3cd; color: #856404; }

.income-statement {
  max-width: 600px;
  margin: 0 auto;
}

.statement-section {
  margin-bottom: 30px;
}

.statement-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.statement-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.statement-total {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-top: 2px solid #333;
  margin-top: 10px;
}

.net-income {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.profit {
  color: #28a745;
}

.loss {
  color: #dc3545;
}

.balance-sheet {
  max-width: 1000px;
  margin: 0 auto;
}

.balance-sheet-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

.bs-column h3 {
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.bs-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.bs-total {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-top: 1px solid #333;
  margin-top: 10px;
}

.final-total {
  border-top: 2px solid #333;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
}

.balance-warning {
  background: #fff3cd;
  color: #856404;
  padding: 12px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
  font-weight: 500;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}
</style>
