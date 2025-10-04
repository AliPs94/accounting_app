import './assets/main.css'
import './assets/rtl.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

// Initialize auth store and load user from storage
const authStore = useAuthStore()
authStore.loadUserFromStorage()

app.mount('#app')
