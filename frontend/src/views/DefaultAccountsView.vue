<template>
  <div class="default-accounts">
    <div class="container">
      <div class="header">
        <h1>{{ $t('defaultAccounts.title') }}</h1>
        <p class="subtitle">{{ $t('defaultAccounts.subtitle') }}</p>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button @click="applyToCurrentAssociation" class="btn-primary" :disabled="isLoading">
          {{ $t('defaultAccounts.applyToCurrent') }}
        </button>
        <button @click="refreshTemplates" class="btn-secondary" :disabled="isLoading">
          {{ $t('defaultAccounts.refresh') }}
        </button>
      </div>

      <!-- Templates List -->
      <div class="templates-section">
        <h2>{{ $t('defaultAccounts.templates') }}</h2>
        
        <div v-if="isLoading" class="loading">
          <div class="loading-spinner"></div>
          <p>{{ $t('defaultAccounts.loading') }}</p>
        </div>

        <div v-else class="templates-grid">
          <div
            v-for="template in templates"
            :key="template.id"
            class="template-card"
          >
            <div class="card-header">
              <span class="template-code">{{ template.code }}</span>
              <span class="template-type">{{ template.account_type }}</span>
            </div>
            <div class="card-content">
              <h3 class="template-name">{{ template.name }}</h3>
              <p class="template-status" :class="{ active: template.is_active, inactive: !template.is_active }">
                {{ template.is_active ? $t('defaultAccounts.active') : $t('defaultAccounts.inactive') }}
              </p>
            </div>
          </div>
        </div>

        <div v-if="!isLoading && templates.length === 0" class="no-templates">
          <div class="no-templates-icon">📋</div>
          <h3>{{ $t('defaultAccounts.noTemplates') }}</h3>
          <p>{{ $t('defaultAccounts.noTemplatesDescription') }}</p>
        </div>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { defaultAccountTemplatesAPI } from '@/services/apiService'

const { t } = useI18n()
const authStore = useAuthStore()

// State
const templates = ref([])
const isLoading = ref(false)
const message = ref('')
const messageType = ref('')

// Methods
const loadTemplates = async () => {
  isLoading.value = true
  try {
    const response = await defaultAccountTemplatesAPI.getAll()
    templates.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load templates:', error)
    showMessage(t('defaultAccounts.failedToLoad'), 'error')
  } finally {
    isLoading.value = false
  }
}

const applyToCurrentAssociation = async () => {
  if (!authStore.user?.association_id) {
    showMessage(t('defaultAccounts.noAssociation'), 'error')
    return
  }

  isLoading.value = true
  try {
    await defaultAccountTemplatesAPI.applyToAssociation(authStore.user.association_id)
    showMessage(t('defaultAccounts.success'), 'success')
  } catch (error) {
    console.error('Failed to apply templates:', error)
    showMessage(t('defaultAccounts.failedToApply'), 'error')
  } finally {
    isLoading.value = false
  }
}

const refreshTemplates = () => {
  loadTemplates()
}

const showMessage = (text, type) => {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
    messageType.value = ''
  }, 5000)
}

// Lifecycle
onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.default-accounts {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  color: #333;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
  margin: 0;
}

.actions {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
  justify-content: center;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background: #e9ecef;
}

.btn-primary:disabled, .btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.templates-section h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.template-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e5e9;
  transition: all 0.3s ease;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.template-code {
  background: #667eea;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.9rem;
}

.template-type {
  background: #f8f9fa;
  color: #666;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.template-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 10px 0;
}

.template-status {
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0;
}

.template-status.active {
  color: #28a745;
}

.template-status.inactive {
  color: #dc3545;
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  color: #666;
  margin: 0;
}

.no-templates {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-templates-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.no-templates h3 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 1.5rem;
}

.no-templates p {
  color: #666;
  margin: 0;
}

.message {
  padding: 15px 20px;
  border-radius: 8px;
  margin: 20px 0;
  font-weight: 500;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Responsive Design */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .actions {
    flex-direction: column;
    align-items: center;
  }
  
  .header h1 {
    font-size: 2rem;
  }
}
</style>
