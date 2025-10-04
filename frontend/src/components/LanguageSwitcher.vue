<template>
  <div class="language-switcher">
    <label for="language-select">{{ $t('common.language') }}:</label>
    <select 
      id="language-select" 
      v-model="currentLocale" 
      @change="changeLanguage"
      class="language-select"
    >
      <option value="ar">العربية</option>
      <option value="en">English</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const currentLocale = ref(locale.value)

const changeLanguage = () => {
  locale.value = currentLocale.value
  localStorage.setItem('locale', currentLocale.value)
  
  // Update document direction
  updateDocumentDirection()
}

const updateDocumentDirection = () => {
  const html = document.documentElement
  if (currentLocale.value === 'ar') {
    html.setAttribute('dir', 'rtl')
    html.setAttribute('lang', 'ar')
  } else {
    html.setAttribute('dir', 'ltr')
    html.setAttribute('lang', 'en')
  }
}

onMounted(() => {
  updateDocumentDirection()
})
</script>

<style scoped>
.language-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  position: relative;
  z-index: 1;
}

.language-switcher label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 12px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.language-select {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 100px;
}

.language-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.2);
}

.language-select:hover {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.language-select option {
  background: #667eea;
  color: white;
  padding: 8px;
}

/* RTL Support for Arabic */
[dir="rtl"] .language-switcher {
  flex-direction: row-reverse;
  direction: rtl;
}

[dir="rtl"] .language-switcher label {
  text-align: right;
  direction: rtl;
}

[dir="rtl"] .language-select {
  text-align: right;
  direction: rtl;
}

[dir="rtl"] .language-select option {
  text-align: right;
  direction: rtl;
}

/* Responsive Design */
@media (max-width: 768px) {
  .language-switcher {
    flex-direction: column;
    gap: 4px;
    align-items: center;
  }
  
  .language-switcher label {
    font-size: 11px;
  }
  
  .language-select {
    font-size: 12px;
    padding: 6px 10px;
    min-width: 80px;
  }
}

@media (max-width: 480px) {
  .language-switcher {
    width: 100%;
  }
  
  .language-select {
    width: 100%;
    text-align: center;
  }
}
</style>
