import { createI18n } from 'vue-i18n'
import ar from './locales/ar.json'
import en from './locales/en.json'

// Get saved locale from localStorage or default to Arabic
const savedLocale = localStorage.getItem('locale') || 'ar'

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: savedLocale, // Default to Arabic
  fallbackLocale: 'en', // Fallback to English
  messages: {
    ar,
    en
  },
  // Global properties
  globalInjection: true,
  // Silent fallback warnings
  silentFallbackWarn: true,
  // Missing key handler
  missingWarn: false,
  fallbackWarn: false
})

export default i18n
