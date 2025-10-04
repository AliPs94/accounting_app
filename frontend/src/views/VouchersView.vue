<template>
  <div class="vouchers">
    <div class="page-header">
      <h1>{{ $t('vouchers.title') }}</h1>
      <router-link to="/vouchers/create" class="btn-primary">
        + {{ $t('vouchers.createVoucher') }}
      </router-link>
    </div>

    <div v-if="isLoading" class="loading">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else-if="vouchers.length === 0" class="empty-state">
      <h3>{{ $t('vouchers.noVouchers') }}</h3>
      <p>{{ $t('vouchers.createFirstVoucher') }}</p>
      <router-link to="/vouchers/create" class="btn-primary">
        {{ $t('vouchers.createFirstVoucher') }}
      </router-link>
    </div>

    <div v-else class="vouchers-list">
      <div v-for="voucher in vouchers" :key="voucher.id" class="voucher-card">
        <div class="voucher-header">
          <div class="voucher-info">
            <h3>{{ voucher.voucher_number }}</h3>
            <p>{{ voucher.description }}</p>
          </div>
          <div class="voucher-meta">
            <span class="voucher-type">{{ voucher.voucher_type }}</span>
            <span class="voucher-date">{{ formatDate(voucher.date) }}</span>
          </div>
        </div>
        
        <div class="voucher-details">
          <div class="detail-summary">
            <span class="detail-count">{{ voucher.details_count }} {{ $t('vouchers.entries') }}</span>
            <span class="total-amount">{{ $t('vouchers.total') }}: ${{ voucher.total_debits.toFixed(2) }}</span>
          </div>
          <div class="voucher-actions">
            <button @click="viewVoucher(voucher)" class="btn-secondary">{{ $t('common.view') }}</button>
            <button @click="editVoucher(voucher)" class="btn-edit">{{ $t('common.edit') }}</button>
            <button @click="deleteVoucher(voucher)" class="btn-delete">{{ $t('common.delete') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { vouchersAPI } from '@/services/apiService'
import type { VoucherList } from '@/types/accounting'

const router = useRouter()
const { t } = useI18n()
const vouchers = ref<VoucherList[]>([])
const isLoading = ref(false)
const error = ref('')

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const loadVouchers = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await vouchersAPI.getAll()
    vouchers.value = response.data.results
  } catch (err: any) {
    error.value = err.response?.data?.error || t('common.failedToLoad') + ' vouchers'
  } finally {
    isLoading.value = false
  }
}

const viewVoucher = (voucher: VoucherList) => {
  // Navigate to voucher detail view (we'll create this)
  router.push(`/vouchers/${voucher.id}`)
}

const editVoucher = (voucher: VoucherList) => {
  // Navigate to voucher edit view
  router.push(`/vouchers/${voucher.id}/edit`)
}

const deleteVoucher = async (voucher: VoucherList) => {
  if (!confirm(`${t('common.confirmDelete')} "${voucher.voucher_number}"?`)) {
    return
  }

  try {
    await vouchersAPI.delete(voucher.id)
    await loadVouchers()
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to delete voucher'
  }
}

onMounted(() => {
  loadVouchers()
})
</script>

<style scoped>
.vouchers {
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

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.empty-state p {
  margin: 0 0 20px 0;
  color: #666;
}

.vouchers-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.voucher-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.voucher-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.voucher-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.voucher-info h3 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 18px;
}

.voucher-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.voucher-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.voucher-type {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.voucher-date {
  color: #999;
  font-size: 12px;
}

.voucher-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.detail-summary {
  display: flex;
  gap: 20px;
  align-items: center;
}

.detail-count {
  color: #666;
  font-size: 14px;
}

.total-amount {
  font-weight: 600;
  color: #28a745;
  font-size: 16px;
}

.voucher-actions {
  display: flex;
  gap: 8px;
}

.voucher-actions button {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .voucher-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .voucher-meta {
    align-items: flex-start;
  }
  
  .voucher-details {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .detail-summary {
    justify-content: space-between;
  }
  
  .voucher-actions {
    justify-content: center;
  }
}
</style>
