<template>
  <div class="voucher-detail">
    <div class="page-header">
      <h1>{{ $t('vouchers.voucherDetails') }}</h1>
      <div class="header-actions">
        <button @click="$router.go(-1)" class="btn-secondary">
          ← {{ $t('vouchers.back') }}
        </button>
        <button @click="editVoucher" class="btn-primary">
          {{ $t('common.edit') }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else-if="voucher" class="voucher-content">
      <!-- Voucher Header -->
      <div class="voucher-header">
        <div class="voucher-info">
          <h2>{{ voucher.voucher_number }}</h2>
          <p class="voucher-description">{{ voucher.description }}</p>
        </div>
        <div class="voucher-meta">
          <div class="meta-item">
            <span class="meta-label">{{ $t('vouchers.date') }}:</span>
            <span class="meta-value">{{ formatDate(voucher.date) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">{{ $t('vouchers.voucherType') }}:</span>
            <span class="meta-value">{{ voucher.voucher_type }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">{{ $t('vouchers.createdBy') }}:</span>
            <span class="meta-value">{{ voucher.created_by_username }}</span>
          </div>
        </div>
      </div>

      <!-- Voucher Details Table -->
      <div class="voucher-details">
        <h3>{{ $t('vouchers.journalEntries') }}</h3>
        <div class="details-table">
          <table>
            <thead>
              <tr>
                <th>{{ $t('vouchers.account') }}</th>
                <th>{{ $t('vouchers.description') }}</th>
                <th class="amount-column">{{ $t('vouchers.debit') }}</th>
                <th class="amount-column">{{ $t('vouchers.credit') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="detail in voucher.details" :key="detail.id">
                <td>
                  <div class="account-info">
                    <span class="account-code">{{ detail.account_code }}</span>
                    <span class="account-name">{{ detail.account_name }}</span>
                  </div>
                </td>
                <td>{{ detail.description }}</td>
                <td class="amount">
                  <span v-if="detail.debit > 0">{{ formatCurrency(detail.debit) }}</span>
                  <span v-else>-</span>
                </td>
                <td class="amount">
                  <span v-if="detail.credit > 0">{{ formatCurrency(detail.credit) }}</span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="totals-row">
                <td colspan="2"><strong>{{ $t('vouchers.total') }}</strong></td>
                <td class="amount"><strong>{{ formatCurrency(voucher.total_debits) }}</strong></td>
                <td class="amount"><strong>{{ formatCurrency(voucher.total_credits) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Balance Status -->
      <div class="balance-status" :class="{ 'balanced': voucher.is_balanced, 'unbalanced': !voucher.is_balanced }">
        <span v-if="voucher.is_balanced" class="status-icon">✓</span>
        <span v-else class="status-icon">⚠</span>
        <span v-if="voucher.is_balanced">{{ $t('vouchers.voucherBalanced') }}</span>
        <span v-else>{{ $t('vouchers.voucherUnbalanced') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { vouchersAPI } from '@/services/apiService'
import type { Voucher } from '@/types/accounting'

const route = useRoute()
const router = useRouter()

const voucher = ref<Voucher | null>(null)
const isLoading = ref(false)
const error = ref('')

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const loadVoucher = async () => {
  const voucherId = route.params.id as string
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await vouchersAPI.getById(parseInt(voucherId))
    voucher.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load voucher'
  } finally {
    isLoading.value = false
  }
}

const editVoucher = () => {
  router.push(`/vouchers/${route.params.id}/edit`)
}

onMounted(() => {
  loadVoucher()
})
</script>

<style scoped>
.voucher-detail {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.voucher-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.voucher-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.voucher-info h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.voucher-description {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.voucher-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  gap: 10px;
}

.meta-label {
  font-weight: 600;
  color: #333;
  min-width: 100px;
}

.meta-value {
  color: #666;
}

.voucher-details h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.details-table {
  overflow-x: auto;
}

.details-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.details-table th,
.details-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.details-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.details-table tr:hover {
  background: #f8f9fa;
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.account-code {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.account-name {
  color: #666;
  font-size: 13px;
}

.amount-column {
  text-align: right;
  width: 120px;
}

.amount {
  text-align: right;
  font-family: monospace;
  font-weight: 500;
}

.totals-row {
  background: #f8f9fa;
  font-weight: 600;
}

.balance-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  border-radius: 6px;
  margin-top: 20px;
  font-weight: 600;
}

.balance-status.balanced {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.balance-status.unbalanced {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.status-icon {
  font-size: 18px;
  font-weight: bold;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  text-align: center;
}

@media (max-width: 768px) {
  .voucher-header {
    flex-direction: column;
    gap: 20px;
  }
  
  .voucher-meta {
    width: 100%;
  }
  
  .details-table {
    font-size: 14px;
  }
  
  .details-table th,
  .details-table td {
    padding: 8px;
  }
}
</style>
