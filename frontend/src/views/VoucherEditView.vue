<template>
  <div class="voucher-edit">
    <div class="page-header">
      <h1>{{ $t('vouchers.editVoucher') }}</h1>
      <button @click="$router.go(-1)" class="btn-secondary">
        ← {{ $t('vouchers.back') }}
      </button>
    </div>

    <div v-if="isLoading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else-if="voucher" class="edit-content">
      <div class="edit-notice">
        <h3>{{ $t('vouchers.editNotice') }}</h3>
        <p>{{ $t('vouchers.editNoticeDescription') }}</p>
        <button @click="navigateToCreate" class="btn-primary">
          {{ $t('vouchers.createNewVoucher') }}
        </button>
      </div>

      <!-- Display current voucher for reference -->
      <div class="current-voucher">
        <h3>{{ $t('vouchers.currentVoucher') }}</h3>
        <div class="voucher-summary">
          <div class="summary-item">
            <span class="label">{{ $t('vouchers.voucherNumber') }}:</span>
            <span class="value">{{ voucher.voucher_number }}</span>
          </div>
          <div class="summary-item">
            <span class="label">{{ $t('vouchers.date') }}:</span>
            <span class="value">{{ formatDate(voucher.date) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">{{ $t('vouchers.voucherType') }}:</span>
            <span class="value">{{ voucher.voucher_type }}</span>
          </div>
          <div class="summary-item">
            <span class="label">{{ $t('vouchers.description') }}:</span>
            <span class="value">{{ voucher.description }}</span>
          </div>
          <div class="summary-item">
            <span class="label">{{ $t('vouchers.total') }}:</span>
            <span class="value">{{ formatCurrency(voucher.total_debits) }}</span>
          </div>
        </div>
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

const navigateToCreate = () => {
  router.push('/vouchers/create')
}

onMounted(() => {
  loadVoucher()
})
</script>

<style scoped>
.voucher-edit {
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

.edit-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.edit-notice {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 30px;
  text-align: center;
}

.edit-notice h3 {
  margin: 0 0 10px 0;
  color: #856404;
}

.edit-notice p {
  margin: 0 0 15px 0;
  color: #856404;
}

.current-voucher {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 20px;
}

.current-voucher h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.voucher-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.value {
  color: #666;
  font-size: 16px;
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
  .voucher-summary {
    grid-template-columns: 1fr;
  }
}
</style>
