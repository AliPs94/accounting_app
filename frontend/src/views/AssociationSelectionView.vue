<template>
  <div class="association-selection">
    <div class="container">
      <div class="header">
        <h1>{{ $t('associationSelection.title') }}</h1>
        <p class="subtitle">{{ $t('associationSelection.subtitle') }}</p>
      </div>

      <!-- Search Section -->
      <div class="search-section">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('associationSelection.searchPlaceholder')"
            class="search-input"
            @input="filterAssociations"
          />
          <div class="search-icon">🔍</div>
        </div>
        <div class="search-filters">
          <label class="filter-label">
            <input
              v-model="searchBy"
              type="radio"
              value="name"
              class="filter-radio"
            />
            {{ $t('associationSelection.searchByName') }}
          </label>
          <label class="filter-label">
            <input
              v-model="searchBy"
              type="radio"
              value="id"
              class="filter-radio"
            />
            {{ $t('associationSelection.searchById') }}
          </label>
        </div>
      </div>

      <!-- Associations Grid -->
      <div class="associations-grid">
        <div
          v-for="association in filteredAssociations"
          :key="association.id"
          class="association-card"
          @click="selectAssociation(association)"
        >
          <div class="card-header">
            <h3 class="association-name">{{ association.name }}</h3>
            <span class="association-id">ID: {{ association.id }}</span>
          </div>
          <div class="card-content">
            <p class="association-description">
              {{ $t('associationSelection.clickToSelect') }}
            </p>
          </div>
          <div class="card-footer">
            <button class="select-btn">
              {{ $t('associationSelection.select') }}
            </button>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-if="filteredAssociations.length === 0" class="no-results">
        <div class="no-results-icon">🔍</div>
        <h3>{{ $t('associationSelection.noResults') }}</h3>
        <p>{{ $t('associationSelection.noResultsDescription') }}</p>
        <button @click="clearSearch" class="clear-search-btn">
          {{ $t('associationSelection.clearSearch') }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading">
        <div class="loading-spinner"></div>
        <p>{{ $t('associationSelection.loading') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { associationsAPI, authAPI } from '@/services/apiService'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

// State
const associations = ref([])
const searchQuery = ref('')
const searchBy = ref('name')
const isLoading = ref(false)

// Computed
const filteredAssociations = computed(() => {
  if (!searchQuery.value.trim()) {
    return associations.value
  }

  const query = searchQuery.value.toLowerCase().trim()
  
  return associations.value.filter(association => {
    if (searchBy.value === 'name') {
      return association.name.toLowerCase().includes(query)
    } else if (searchBy.value === 'id') {
      return association.id.toString().includes(query)
    }
    return false
  })
})

// Methods
const loadAssociations = async () => {
  isLoading.value = true
  try {
    const response = await associationsAPI.getAll()
    associations.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load associations:', error)
    alert(t('associationSelection.failedToLoad'))
  } finally {
    isLoading.value = false
  }
}

const filterAssociations = () => {
  // This is handled by the computed property
}

const selectAssociation = async (association) => {
  try {
    await authAPI.switchAssociation(association.id)
    
    // Update user store with new association
    const profileResponse = await authAPI.getProfile()
    authStore.setUser(profileResponse.data.user)
    
    // Redirect to dashboard
    router.push('/')
  } catch (error) {
    console.error('Failed to select association:', error)
    alert(t('associationSelection.failedToSelect'))
  }
}

const clearSearch = () => {
  searchQuery.value = ''
}

// Lifecycle
onMounted(() => {
  loadAssociations()
})
</script>

<style scoped>
.association-selection {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  color: white;
}

.header h1 {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.subtitle {
  font-size: 1.2rem;
  margin: 0;
  opacity: 0.9;
}

.search-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.search-box {
  position: relative;
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 15px 50px 15px 20px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
  color: #666;
}

.search-filters {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #333;
}

.filter-radio {
  margin: 0;
}

.associations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.association-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.association-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.card-header {
  margin-bottom: 15px;
}

.association-name {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 5px 0;
}

.association-id {
  font-size: 0.9rem;
  color: #666;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.card-content {
  margin-bottom: 20px;
}

.association-description {
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.card-footer {
  text-align: center;
}

.select-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.select-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.no-results-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.no-results h3 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 1.5rem;
}

.no-results p {
  color: #666;
  margin: 0 0 20px 0;
}

.clear-search-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.clear-search-btn:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.loading {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
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
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .associations-grid {
    grid-template-columns: 1fr;
  }
  
  .search-filters {
    flex-direction: column;
    gap: 10px;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
}
</style>
