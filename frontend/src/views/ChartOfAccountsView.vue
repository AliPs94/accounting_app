<template>
  <div class="chart-of-accounts">
    <div class="page-header">
      <h1>{{ $t('accounts.title') }}</h1>
      <button @click="openCreateModal" class="btn-primary">
        <span>+</span> {{ $t('accounts.addAccount') }}
      </button>
    </div>

    <div class="filters">
      <select v-model="selectedType" @change="filterAccounts" class="filter-select">
        <option value="">{{ $t('accounts.allAccountTypes') }}</option>
        <option value="Asset">{{ $t('accounts.assets') }}</option>
        <option value="Liability">{{ $t('accounts.liabilities') }}</option>
        <option value="Equity">{{ $t('accounts.equity') }}</option>
        <option value="Revenue">{{ $t('accounts.revenue') }}</option>
        <option value="Expense">{{ $t('accounts.expenses') }}</option>
      </select>
      
      <button @click="loadHierarchy" class="btn-secondary">
        {{ $t('accounts.showHierarchy') }}
      </button>
    </div>

    <div v-if="isLoading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else class="accounts-container">
      <div v-if="showHierarchy" class="hierarchy-view">
        <div v-for="account in hierarchyAccounts" :key="account.id" class="account-tree">
          <AccountTreeNode :account="account" :level="0" @edit="openEditModal" @delete="deleteAccount" />
        </div>
      </div>

      <div v-else class="table-view">
        <table class="accounts-table">
          <thead>
            <tr>
              <th>{{ $t('accounts.accountCode') }}</th>
              <th>{{ $t('accounts.accountName') }}</th>
              <th>{{ $t('accounts.accountType') }}</th>
              <th>{{ $t('accounts.parentAccount') }}</th>
              <th>{{ $t('common.status') }}</th>
              <th>{{ $t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in filteredAccounts" :key="account.id">
              <td>{{ account.code }}</td>
              <td>{{ account.name }}</td>
              <td>
                <span :class="`account-type-badge ${account.account_type.toLowerCase()}`">
                  {{ $t('accounts.accountTypes.' + account.account_type) }}
                </span>
              </td>
              <td>{{ account.parent_name || '-' }}</td>
              <td>
                <span :class="`status-badge ${account.is_active ? 'active' : 'inactive'}`">
                  {{ account.is_active ? $t('accounts.active') : $t('accounts.inactive') }}
                </span>
              </td>
              <td>
                <button @click="openEditModal(account)" class="btn-edit">{{ $t('common.edit') }}</button>
                <button @click="deleteAccount(account)" class="btn-delete">{{ $t('common.delete') }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Account Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ isEditing ? $t('accounts.editAccount') : $t('accounts.addAccount') }}</h2>
          <button @click="closeModal" class="modal-close">&times;</button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label for="code">{{ $t('accounts.accountCode') }} *</label>
            <input
              id="code"
              v-model="formData.code"
              type="text"
              required
              :disabled="isEditing"
              placeholder="e.g., 1000"
            />
          </div>

          <div class="form-group">
            <label for="name">{{ $t('accounts.accountName') }} *</label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              required
              placeholder="e.g., Cash"
            />
          </div>

          <div class="form-group">
            <label for="account_type">{{ $t('accounts.accountType') }} *</label>
            <select id="account_type" v-model="formData.account_type" required>
              <option value="">{{ $t('common.select') }}</option>
              <option value="Asset">{{ $t('accounts.accountTypes.Asset') }}</option>
              <option value="Liability">{{ $t('accounts.accountTypes.Liability') }}</option>
              <option value="Equity">{{ $t('accounts.accountTypes.Equity') }}</option>
              <option value="Revenue">{{ $t('accounts.accountTypes.Revenue') }}</option>
              <option value="Expense">{{ $t('accounts.accountTypes.Expense') }}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="parent">{{ $t('accounts.parentAccount') }}</label>
            <select id="parent" v-model="formData.parent">
              <option value="">{{ $t('accounts.noParent') }}</option>
              <option v-for="account in availableParents" :key="account.id" :value="account.id">
                {{ account.code }} - {{ account.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.is_active"
                type="checkbox"
              />
              {{ $t('accounts.active') }}
            </label>
          </div>

          <div v-if="formError" class="form-error">
            {{ formError }}
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel">
              {{ $t('accounts.cancel') }}
            </button>
            <button type="submit" :disabled="isSubmitting" class="btn-primary">
              {{ isSubmitting ? $t('accounts.saving') : (isEditing ? $t('accounts.update') : $t('accounts.create')) }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { accountsAPI } from '@/services/apiService'
import type { Account, CreateAccountData } from '@/types/accounting'
import AccountTreeNode from '@/components/AccountTreeNode.vue'

// State
const accounts = ref<Account[]>([])
const hierarchyAccounts = ref<Account[]>([])
const isLoading = ref(false)
const error = ref('')
const showHierarchy = ref(false)
const selectedType = ref('')

// Modal state
const showModal = ref(false)
const isEditing = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const editingAccount = ref<Account | null>(null)

const formData = reactive<CreateAccountData>({
  name: '',
  account_type: '' as any,
  parent: undefined,
  code: '',
  is_active: true
})

// Computed
const filteredAccounts = computed(() => {
  if (!selectedType.value) return accounts.value
  return accounts.value.filter(account => account.account_type === selectedType.value)
})

const availableParents = computed(() => {
  return accounts.value.filter(account => 
    account.is_active && 
    (!isEditing.value || account.id !== editingAccount.value?.id)
  )
})

// Methods
const loadAccounts = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await accountsAPI.getAll()
    accounts.value = response.data.results
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load accounts'
  } finally {
    isLoading.value = false
  }
}

const loadHierarchy = async () => {
  try {
    const response = await accountsAPI.getHierarchy()
    hierarchyAccounts.value = response.data
    showHierarchy.value = true
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load hierarchy'
  }
}

const filterAccounts = () => {
  showHierarchy.value = false
}

const openCreateModal = () => {
  isEditing.value = false
  editingAccount.value = null
  resetForm()
  showModal.value = true
}

const openEditModal = (account: Account) => {
  isEditing.value = true
  editingAccount.value = account
  formData.name = account.name
  formData.account_type = account.account_type
  formData.parent = account.parent || undefined
  formData.code = account.code
  formData.is_active = account.is_active
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  formError.value = ''
  resetForm()
}

const resetForm = () => {
  formData.name = ''
  formData.account_type = '' as any
  formData.parent = undefined
  formData.code = ''
  formData.is_active = true
}

const handleSubmit = async () => {
  if (!formData.name || !formData.account_type || !formData.code) {
    formError.value = 'Please fill in all required fields'
    return
  }

  isSubmitting.value = true
  formError.value = ''

  try {
    console.log('Submitting account data:', formData)
    
    if (isEditing.value && editingAccount.value) {
      console.log('Updating account:', editingAccount.value.id)
      await accountsAPI.update(editingAccount.value.id, formData)
    } else {
      console.log('Creating new account')
      await accountsAPI.create(formData)
    }
    
    closeModal()
    await loadAccounts()
  } catch (err: any) {
    console.error('Account creation/update error:', err)
    console.error('Error response:', err.response?.data)
    
    if (err.response?.data?.details) {
      formError.value = `Validation Error: ${JSON.stringify(err.response.data.details)}`
    } else if (err.response?.data?.error) {
      formError.value = err.response.data.error
    } else if (err.response?.data?.detail) {
      formError.value = err.response.data.detail
    } else {
      formError.value = 'Failed to save account'
    }
  } finally {
    isSubmitting.value = false
  }
}

const deleteAccount = async (account: Account) => {
  if (!confirm(`Are you sure you want to delete account "${account.name}"?`)) {
    return
  }

  try {
    await accountsAPI.delete(account.id)
    await loadAccounts()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to delete account'
  }
}

// Lifecycle
onMounted(() => {
  loadAccounts()
})
</script>

<style scoped>
.chart-of-accounts {
  padding: 20px;
  max-width: 1200px;
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

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary, .btn-secondary, .btn-edit, .btn-delete, .btn-cancel {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-edit {
  background: #28a745;
  color: white;
  margin-right: 5px;
}

.btn-edit:hover {
  background: #1e7e34;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.btn-delete:hover {
  background: #c82333;
}

.btn-cancel {
  background: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background: #545b62;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 16px;
}

.error {
  color: #dc3545;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.accounts-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.accounts-table th,
.accounts-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.accounts-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.accounts-table tr:hover {
  background: #f8f9fa;
}

.account-type-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.account-type-badge.asset { background: #d4edda; color: #155724; }
.account-type-badge.liability { background: #f8d7da; color: #721c24; }
.account-type-badge.equity { background: #d1ecf1; color: #0c5460; }
.account-type-badge.revenue { background: #d4edda; color: #155724; }
.account-type-badge.expense { background: #fff3cd; color: #856404; }

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active { background: #d4edda; color: #155724; }
.status-badge.inactive { background: #f8d7da; color: #721c24; }

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-close:hover {
  color: #333;
}

.modal-form {
  padding: 20px;
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
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.form-error {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.hierarchy-view {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .chart-of-accounts {
    padding: 15px;
  }
  
  .filters {
    gap: 10px;
  }
}

@media (max-width: 768px) {
  .chart-of-accounts {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .filters {
    flex-direction: column;
    gap: 10px;
  }
  
  .filter-select,
  .btn-secondary {
    width: 100%;
  }
  
  /* Table responsive */
  .accounts-table {
    font-size: 14px;
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .accounts-table thead {
    display: none;
  }
  
  .accounts-table tbody,
  .accounts-table tr,
  .accounts-table td {
    display: block;
  }
  
  .accounts-table tr {
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    background: white;
  }
  
  .accounts-table td {
    text-align: left !important;
    padding: 8px 0;
    border: none;
    position: relative;
    padding-left: 50%;
  }
  
  .accounts-table td:before {
    content: attr(data-label);
    position: absolute;
    left: 0;
    width: 45%;
    padding-right: 10px;
    font-weight: 600;
    text-align: left;
  }
  
  .accounts-table td:nth-child(1):before {
    content: "Code: ";
  }
  
  .accounts-table td:nth-child(2):before {
    content: "Name: ";
  }
  
  .accounts-table td:nth-child(3):before {
    content: "Type: ";
  }
  
  .accounts-table td:nth-child(4):before {
    content: "Parent: ";
  }
  
  .accounts-table td:nth-child(5):before {
    content: "Status: ";
  }
  
  .accounts-table td:nth-child(6):before {
    content: "Actions: ";
  }
  
  .accounts-table td:nth-child(6) {
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
    padding-left: 0;
  }
  
  .btn-edit,
  .btn-delete {
    flex: 1;
    min-width: 80px;
  }
  
  /* Modal responsive */
  .modal-content {
    width: 95%;
    max-width: 500px;
    margin: 20px;
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .modal-header h2 {
    font-size: 20px;
  }
  
  .modal-actions {
    flex-direction: column-reverse;
    gap: 10px;
  }
  
  .modal-actions button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 20px;
  }
  
  .btn-primary {
    width: 100%;
    padding: 12px;
  }
  
  .accounts-table {
    font-size: 13px;
  }
  
  .accounts-table tr {
    padding: 12px;
  }
  
  .accounts-table td {
    padding: 6px 0;
    padding-left: 45%;
  }
  
  .modal-content {
    width: 100%;
    margin: 10px;
    padding: 20px 15px;
  }
  
  .form-group label {
    font-size: 14px;
  }
  
  .form-group input,
  .form-group select {
    font-size: 14px;
  }
}
</style>
