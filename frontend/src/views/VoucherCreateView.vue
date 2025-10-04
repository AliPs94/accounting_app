<template>
  <div class="voucher-create">
    <div class="page-header">
      <h1>{{ $t('vouchers.createVoucher') }}</h1>
      <button @click="$router.go(-1)" class="btn-secondary">
        ← {{ $t('vouchers.back') }}
      </button>
    </div>

    <form @submit.prevent="handleSubmit" class="voucher-form">
      <!-- Voucher Header -->
      <div class="form-section">
        <h2>{{ $t('vouchers.voucherDetails') }}</h2>
        <div class="form-row">
          <div class="form-group">
            <label for="date">{{ $t('vouchers.date') }} *</label>
            <input
              id="date"
              v-model="voucherData.date"
              type="date"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="voucher_type">{{ $t('vouchers.voucherType') }} *</label>
            <select id="voucher_type" v-model="voucherData.voucher_type" @change="onVoucherTypeChange" required>
              <option value="">{{ $t('common.select') }}</option>
              <option value="Payment">{{ $t('vouchers.voucherTypes.Payment') }}</option>
              <option value="Receipt">{{ $t('vouchers.voucherTypes.Receipt') }}</option>
              <option value="Journal">{{ $t('vouchers.voucherTypes.Journal') }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="voucher_number">{{ $t('vouchers.voucherNumber') }} *</label>
            <input
              id="voucher_number"
              v-model="voucherData.voucher_number"
              type="text"
              required
              :placeholder="suggestedVoucherNumber || 'e.g., JV-001'"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="description">{{ $t('vouchers.description') }} *</label>
          <textarea
            id="description"
            v-model="voucherData.description"
            required
            rows="3"
            :placeholder="$t('vouchers.description')"
          ></textarea>
        </div>
      </div>

      <!-- Voucher Details -->
      <div class="form-section">
        <div class="section-header">
          <h2>{{ $t('vouchers.entriesHeaders.' + voucherData.voucher_type) }}</h2>
          <button type="button" @click="addTransactionLine" class="btn-primary">
            + {{ $t('vouchers.addTransaction') }}
          </button>
        </div>

        <div v-if="voucherData.transactions.length === 0" class="empty-state">
          <p>{{ $t('vouchers.noTransactions') }}</p>
        </div>

        <div v-else class="transactions-container">
          <div v-for="(transaction, index) in voucherData.transactions" :key="index" class="transaction-card">
            <div class="transaction-header">
              <h3>{{ $t('vouchers.transaction') }} {{ index + 1 }}</h3>
              <button
                type="button"
                @click="removeTransactionLine(index)"
                class="btn-delete"
                :disabled="voucherData.transactions.length <= 1"
              >
                {{ $t('common.delete') }}
              </button>
            </div>
            
            <div class="transaction-content">
              <div class="transaction-row">
                <div class="transaction-number-group">
                  <label>{{ $t('vouchers.transactionNumber') || 'Transaction #' }}</label>
                  <input
                    v-model.number="transaction.transactionNumber"
                    type="number"
                    min="1"
                    required
                    class="transaction-number-input"
                  />
                </div>
                
                <div class="account-group">
                  <label>{{ $t('vouchers.fromAccount') }}</label>
                  <select v-model="transaction.fromAccount" required>
                    <option value="">{{ $t('vouchers.selectAccount') }}</option>
                    <option v-for="account in accounts" :key="account.id" :value="account.id">
                      {{ account.code }} - {{ account.name }}
                    </option>
                  </select>
                </div>
                
                <div class="amount-group">
                  <label>{{ $t('vouchers.amount') }}</label>
                  <input
                    v-model.number="transaction.amount"
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    required
                    @input="updateTransactionAmounts(index)"
                  />
                </div>
                
                <div class="account-group">
                  <label>{{ $t('vouchers.toAccount') }}</label>
                  <select v-model="transaction.toAccount" required>
                    <option value="">{{ $t('vouchers.selectAccount') }}</option>
                    <option v-for="account in accounts" :key="account.id" :value="account.id">
                      {{ account.code }} - {{ account.name }}
                    </option>
                  </select>
                </div>
              </div>
              
              <div class="transaction-description">
                <label>{{ $t('vouchers.description') }}</label>
                <input
                  v-model="transaction.description"
                  type="text"
                  :placeholder="$t('vouchers.transactionDescription')"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Totals -->
        <div class="totals-section">
          <div class="totals-row">
            <span class="total-label">{{ $t('vouchers.totalDebits') }}:</span>
            <span class="total-amount" :class="{ 'error': !isBalanced }">
              ${{ totalDebits.toFixed(2) }}
            </span>
          </div>
          <div class="totals-row">
            <span class="total-label">{{ $t('vouchers.totalCredits') }}:</span>
            <span class="total-amount" :class="{ 'error': !isBalanced }">
              ${{ totalCredits.toFixed(2) }}
            </span>
          </div>
          <div class="totals-row balance-row">
            <span class="total-label">{{ $t('vouchers.balance') }}:</span>
            <span class="total-amount" :class="{ 'error': !isBalanced, 'success': isBalanced }">
              ${{ balance.toFixed(2) }}
            </span>
          </div>
        </div>

        <div v-if="!isBalanced" class="balance-error">
          ⚠️ {{ $t('vouchers.voucherMustBeBalanced') }}
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="$router.go(-1)" class="btn-cancel">
          {{ $t('common.cancel') }}
        </button>
        <button
          type="submit"
          :disabled="!canSubmit"
          class="btn-primary"
        >
          {{ isSubmitting ? $t('vouchers.creating') : $t('vouchers.create') }}
        </button>
      </div>

      <div v-if="formError" class="form-error">
        {{ formError }}t
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { accountsAPI, vouchersAPI } from '@/services/apiService'
import type { Account, CreateVoucherData } from '@/types/accounting'

const router = useRouter()
const { t } = useI18n()

// State
const accounts = ref<Account[]>([])
const isLoading = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const suggestedVoucherNumber = ref('')

const voucherData = reactive({
  date: new Date().toISOString().split('T')[0],
  description: '',
  voucher_type: 'Journal',
  voucher_number: '',
  transactions: [
    { transactionNumber: 1, fromAccount: 0, toAccount: 0, amount: 0, description: '' }
  ]
})

// Computed
const totalDebits = computed(() => {
  return voucherData.transactions.reduce((sum, transaction) => sum + (transaction.amount || 0), 0)
})

const totalCredits = computed(() => {
  return voucherData.transactions.reduce((sum, transaction) => sum + (transaction.amount || 0), 0)
})

const balance = computed(() => {
  return totalDebits.value - totalCredits.value
})

const isBalanced = computed(() => {
  return Math.abs(balance.value) < 0.01 // Allow for small floating point differences
})

const canSubmit = computed(() => {
  return (
    voucherData.date &&
    voucherData.description &&
    voucherData.voucher_type &&
    voucherData.voucher_number &&
    voucherData.transactions.length >= 1 &&
    voucherData.transactions.every(transaction => 
      transaction.fromAccount > 0 && 
      transaction.toAccount > 0 && 
      transaction.amount > 0 &&
      transaction.fromAccount !== transaction.toAccount
    ) &&
    !isSubmitting.value
  )
})

// Methods
const loadAccounts = async () => {
  isLoading.value = true
  try {
    const response = await accountsAPI.getAll()
    accounts.value = response.data.results.filter((account: Account) => account.is_active)
  } catch (err: any) {
    formError.value = err.response?.data?.error || t('accounts.failedToLoad')
  } finally {
    isLoading.value = false
  }
}

const fetchNextVoucherNumber = async (voucherType: string) => {
  if (!voucherType) return
  
  try {
    const response = await vouchersAPI.getNextVoucherNumber(voucherType)
    suggestedVoucherNumber.value = response.data.suggested_number
    
    // Auto-populate the voucher number field if it's empty
    if (!voucherData.voucher_number) {
      voucherData.voucher_number = response.data.suggested_number
    }
  } catch (err: any) {
    console.error('Failed to fetch next voucher number:', err)
    // Don't show error to user, just keep the field empty
  }
}

const onVoucherTypeChange = () => {
  // Fetch the next suggested voucher number when type changes
  fetchNextVoucherNumber(voucherData.voucher_type)
}

const addTransactionLine = () => {
  // Get the highest transaction number from existing transactions
  const maxTransactionNumber = voucherData.transactions.reduce((max, t) => {
    return t.transactionNumber > max ? t.transactionNumber : max
  }, 0)
  
  // Add new transaction with incremented number
  voucherData.transactions.push({
    transactionNumber: maxTransactionNumber + 1,
    fromAccount: 0,
    toAccount: 0,
    amount: 0,
    description: ''
  })
}

const removeTransactionLine = (index: number) => {
  if (voucherData.transactions.length > 1) {
    voucherData.transactions.splice(index, 1)
    // Optionally renumber remaining transactions to keep them sequential
    // Comment out the next 3 lines if you want to preserve original numbers
    voucherData.transactions.forEach((transaction, idx) => {
      transaction.transactionNumber = idx + 1
    })
  }
}

const updateTransactionAmounts = (index: number) => {
  // This method is called when amount changes
  // The transaction is automatically balanced since we have from/to accounts
}

const handleSubmit = async () => {
  if (!canSubmit.value) return

  isSubmitting.value = true
  formError.value = ''

  try {
    // Convert transactions to backend format (debit/credit entries)
    const details = []
    
    voucherData.transactions.forEach(transaction => {
      if (transaction.fromAccount > 0 && transaction.toAccount > 0 && transaction.amount > 0) {
        // Validate that accounts exist
        const fromAccountExists = accounts.value.some(acc => acc.id === transaction.fromAccount)
        const toAccountExists = accounts.value.some(acc => acc.id === transaction.toAccount)
        
        if (!fromAccountExists) {
          throw new Error(`From account with ID ${transaction.fromAccount} not found`)
        }
        if (!toAccountExists) {
          throw new Error(`To account with ID ${transaction.toAccount} not found`)
        }
        
        // Add debit entry (from account)
        details.push({
          account: Number(transaction.fromAccount),
          debit: Number(transaction.amount),
          credit: 0,
          description: transaction.description || `Transfer to ${getAccountName(transaction.toAccount)}`
        })
        
        // Add credit entry (to account)
        details.push({
          account: Number(transaction.toAccount),
          debit: 0,
          credit: Number(transaction.amount),
          description: transaction.description || `Transfer from ${getAccountName(transaction.fromAccount)}`
        })
      }
    })

    if (details.length === 0) {
      throw new Error('At least one transaction is required')
    }

    const submitData = {
      date: voucherData.date,
      description: voucherData.description,
      voucher_type: voucherData.voucher_type,
      voucher_number: voucherData.voucher_number,
      details
    }

    console.log('Submitting voucher data:', submitData)
    console.log('Details array:', details)
    
    await vouchersAPI.create(submitData)
    router.push('/vouchers')
  } catch (err: any) {
    console.error('Voucher creation error:', err)
    console.error('Error response:', err.response?.data)
    
    if (err.response?.data?.details) {
      formError.value = `${t('common.validationError')}: ${JSON.stringify(err.response.data.details)}`
    } else if (err.response?.data?.error) {
      formError.value = err.response.data.error
    } else if (err.response?.data?.detail) {
      formError.value = err.response.data.detail
    } else {
      formError.value = t('vouchers.failedToCreate')
    }
  } finally {
    isSubmitting.value = false
  }
}

const getAccountName = (accountId: number) => {
  const account = accounts.value.find(acc => acc.id === accountId)
  return account ? `${account.code} - ${account.name}` : t('common.unknownAccount')
}

// Lifecycle
onMounted(() => {
  loadAccounts()
  // Fetch initial voucher number for the default type (Journal)
  fetchNextVoucherNumber(voucherData.voucher_type)
})
</script>

<style scoped>
.voucher-create {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: #333;
}

.voucher-form {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-section {
  margin-bottom: 40px;
}

.form-section h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f8f9fa;
  border-radius: 4px;
  border: 2px dashed #ddd;
}

.transactions-container {
  margin-bottom: 20px;
}

.transaction-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.transaction-header {
  background: #e9ecef;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dee2e6;
}

.transaction-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.transaction-content {
  padding: 20px;
}

.transaction-row {
  display: grid;
  grid-template-columns: 80px 1fr auto 1fr;
  gap: 20px;
  align-items: end;
  margin-bottom: 15px;
}

.transaction-number-group {
  display: flex;
  flex-direction: column;
}

.transaction-number-group label {
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
  font-size: 14px;
}

.transaction-number-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  font-weight: 600;
  background: #f8f9fa;
}

.transaction-number-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.account-group {
  display: flex;
  flex-direction: column;
}

.account-group label {
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
  font-size: 14px;
}

.account-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.account-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.amount-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
}

.amount-group label {
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
  font-size: 14px;
}

.amount-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  font-weight: 600;
  color: #007bff;
}

.amount-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.transaction-description {
  margin-top: 15px;
}

.transaction-description label {
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
  font-size: 14px;
}

.transaction-description input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.transaction-description input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* RTL Support for transaction cards */
[dir="rtl"] .transaction-row {
  direction: rtl;
}

[dir="rtl"] .transaction-header {
  flex-direction: row-reverse;
}

[dir="rtl"] .account-group select,
[dir="rtl"] .amount-group input,
[dir="rtl"] .transaction-description input {
  text-align: right;
}

[dir="rtl"] .amount-group input,
[dir="rtl"] .transaction-number-input {
  text-align: center;
}

.totals-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.totals-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.totals-row:last-child {
  margin-bottom: 0;
}

.balance-row {
  border-top: 1px solid #ddd;
  padding-top: 10px;
  font-weight: 600;
  font-size: 16px;
}

.total-label {
  color: #333;
}

.total-amount {
  font-weight: 600;
  color: #333;
}

.total-amount.error {
  color: #dc3545;
}

.total-amount.success {
  color: #28a745;
}

.balance-error {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.form-error {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-top: 20px;
  font-size: 14px;
}

.btn-primary, .btn-secondary, .btn-delete, .btn-cancel {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-delete {
  background: #dc3545;
  color: white;
  padding: 6px 12px;
  font-size: 12px;
}

.btn-delete:hover:not(:disabled) {
  background: #c82333;
}

.btn-delete:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background: #545b62;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .voucher-create {
    padding: 15px;
  }
  
  .form-row {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .voucher-create {
    padding: 10px;
    max-width: 100%;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .voucher-form {
    padding: 20px 15px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .transaction-row {
    grid-template-columns: 60px 1fr;
    gap: 10px;
  }
  
  .transaction-number-group {
    grid-column: 1;
  }
  
  .account-group:first-of-type {
    grid-column: 2;
  }
  
  .amount-group {
    grid-column: 1 / -1;
    min-width: 100%;
  }
  
  .account-group:last-of-type {
    grid-column: 1 / -1;
  }
  
  .transaction-description {
    margin-top: 10px;
  }
  
  .totals-section {
    padding: 15px;
  }
  
  .form-actions {
    flex-direction: column-reverse;
    gap: 10px;
  }
  
  .form-actions button {
    width: 100%;
  }
  
  .transaction-card {
    margin-bottom: 15px;
  }
  
  .transaction-header h3 {
    font-size: 14px;
  }
  
  .btn-delete {
    padding: 4px 8px;
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 20px;
  }
  
  .form-section h2 {
    font-size: 18px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .section-header button {
    width: 100%;
  }
  
  .transaction-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .transaction-number-group,
  .account-group,
  .amount-group {
    grid-column: 1;
    width: 100%;
  }
  
  .totals-row {
    font-size: 14px;
  }
  
  .balance-row {
    font-size: 15px;
  }
}
</style>
