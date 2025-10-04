<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Navigation from '@/components/Navigation.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { useI18n } from 'vue-i18n'
import { onMounted, onUnmounted, watch, ref } from 'vue'

const authStore = useAuthStore()
const { locale, t } = useI18n()
const showScrollToTop = ref(false)

// Function to update document direction and title based on locale
const updateDocumentDirection = () => {
  const html = document.documentElement
  if (locale.value === 'ar') {
    html.setAttribute('dir', 'rtl')
    html.setAttribute('lang', 'ar')
  } else {
    html.setAttribute('dir', 'ltr')
    html.setAttribute('lang', 'en')
  }
  // Update page title
  document.title = t('app.title')
}

// Scroll to top function
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// Handle scroll event to show/hide scroll to top button
const handleScroll = () => {
  showScrollToTop.value = window.scrollY > 300
}

// Watch for locale changes
watch(locale, () => {
  updateDocumentDirection()
})

onMounted(() => {
  updateDocumentDirection()
  // Add scroll event listener
  window.addEventListener('scroll', handleScroll)
})

// Cleanup scroll listener when component unmounts
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div id="app">
    <Navigation v-if="authStore.isAuthenticated" />
    <RouterView />
    <!-- Scroll to top button -->
    <button 
      v-if="showScrollToTop" 
      @click="scrollToTop" 
      class="scroll-to-top"
      :class="{ 'rtl': locale === 'ar' }"
    >
      ↑
    </button>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  font-size: 16px;
  line-height: 1.5;
  -webkit-text-size-adjust: 100%;
  -ms-text-size-adjust: 100%;
  /* Ensure smooth scrolling */
  scroll-behavior: smooth;
  /* Allow proper scrolling */
  overflow-y: auto;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  width: 100%;
  display: block;
  /* Ensure proper scrolling behavior */
  position: relative;
  overflow-y: auto;
}

/* Ensure proper desktop rendering */
@media (min-width: 768px) {
  body {
    font-size: 16px;
  }
  
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* Global button styles */
.btn-primary, .btn-secondary, .btn-edit, .btn-delete, .btn-cancel {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
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

/* Form styles */
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
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* Error and success messages */
.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin: 10px 0;
  border: 1px solid #f5c6cb;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 4px;
  margin: 10px 0;
  border: 1px solid #c3e6cb;
}

/* Loading states */
.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

/* Card styles */
.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

/* Table styles */
.table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table th,
.table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.table tr:hover {
  background: #f8f9fa;
}

/* Scroll to top button */
.scroll-to-top {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  border: none;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scroll-to-top:hover {
  background: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.scroll-to-top.rtl {
  right: auto;
  left: 20px;
}

/* Responsive design */
@media (max-width: 768px) {
  .navigation {
    flex-direction: column;
    height: auto;
    padding: 15px;
  }
  
  .nav-links {
    flex-wrap: wrap;
    gap: 15px;
    margin: 15px 0;
  }
  
  .nav-user {
    margin-top: 15px;
  }
  
  .scroll-to-top {
    width: 45px;
    height: 45px;
    font-size: 18px;
    bottom: 15px;
    right: 15px;
  }
  
  .scroll-to-top.rtl {
    right: auto;
    left: 15px;
  }
}
</style>
