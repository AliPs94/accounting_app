<template>
  <nav class="navigation">
    <div class="nav-brand">
      <h2>{{ $t('app.title') }}</h2>
    </div>
    
    <div class="nav-links">
      <router-link to="/" class="nav-link">{{ $t('navigation.dashboard') }}</router-link>
      <router-link to="/chart-of-accounts" class="nav-link">{{ $t('navigation.chartOfAccounts') }}</router-link>
      <router-link to="/vouchers" class="nav-link">{{ $t('navigation.vouchers') }}</router-link>
      <router-link to="/reports" class="nav-link">{{ $t('navigation.reports') }}</router-link>
      <router-link to="/default-accounts" class="nav-link">{{ $t('navigation.defaultAccounts') }}</router-link>
    </div>
    
    <div class="nav-user">
      <LanguageSwitcher />
      <span class="user-name">{{ authStore.userFullName }}</span>
      <button @click="handleSwitchAssociation" class="switch-association-btn">{{ $t('navigation.switchAssociation') }}</button>
      <button @click="handleLogout" class="logout-btn">{{ $t('auth.logout') }}</button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const router = useRouter()
const authStore = useAuthStore()

const handleSwitchAssociation = () => {
  router.push('/select-association')
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  height: 70px;
  position: relative;
  overflow: hidden;
}

.navigation::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  z-index: 0;
}

.nav-brand {
  position: relative;
  z-index: 1;
}

.nav-brand h2 {
  margin: 0;
  color: white;
  font-size: 24px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.nav-link {
  text-decoration: none;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  padding: 12px 20px;
  border-radius: 25px;
  transition: all 0.3s ease;
  font-size: 14px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.nav-link:hover::before {
  left: 100%;
}

.nav-link:hover {
  color: white;
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.nav-link.router-link-active {
  color: white;
  background: rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  transform: translateY(-1px);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.user-name {
  color: white;
  font-weight: 600;
  font-size: 14px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.switch-association-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.switch-association-btn:hover {
  background: linear-gradient(135deg, #218838, #1ea085);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.logout-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #dc3545, #e74c3c);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.logout-btn:hover {
  background: linear-gradient(135deg, #c82333, #c0392b);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
}

/* RTL Support for Arabic - Right to Left Layout */
[dir="rtl"] .navigation {
  flex-direction: row-reverse;
  direction: rtl;
}

[dir="rtl"] .nav-brand {
  order: 3; /* Move brand to the right */
}

[dir="rtl"] .nav-links {
  order: 2; /* Keep links in center */
  flex-direction: row-reverse;
  direction: rtl;
}

[dir="rtl"] .nav-user {
  order: 1; /* Move user controls to the left */
  flex-direction: row-reverse;
  direction: rtl;
}

[dir="rtl"] .nav-link {
  text-align: center;
  direction: rtl;
}

[dir="rtl"] .nav-brand h2 {
  text-align: right;
  direction: rtl;
}

[dir="rtl"] .user-name {
  text-align: right;
  direction: rtl;
}

[dir="rtl"] .language-switcher {
  direction: rtl;
}

[dir="rtl"] .switch-association-btn,
[dir="rtl"] .logout-btn {
  direction: rtl;
  text-align: center;
}

/* Additional RTL spacing and alignment */
[dir="rtl"] .navigation {
  padding: 0 20px;
}

[dir="rtl"] .nav-links .nav-link:first-child {
  margin-right: 0;
  margin-left: 0;
}

[dir="rtl"] .nav-links .nav-link:last-child {
  margin-left: 0;
  margin-right: 0;
}

/* RTL hover effects */
[dir="rtl"] .nav-link::before {
  left: 100%;
  right: -100%;
  background: linear-gradient(270deg, transparent, rgba(255, 255, 255, 0.2), transparent);
}

[dir="rtl"] .nav-link:hover::before {
  left: -100%;
  right: 100%;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .nav-links {
    gap: 4px;
  }
  
  .nav-link {
    padding: 10px 16px;
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .navigation {
    flex-direction: column;
    height: auto;
    padding: 15px;
    gap: 15px;
  }
  
  .nav-links {
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
  }
  
  .nav-user {
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
  }
  
  .nav-brand h2 {
    font-size: 20px;
    text-align: center;
  }
  
  .nav-link {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .user-name {
    font-size: 12px;
    padding: 6px 12px;
  }
  
  .switch-association-btn,
  .logout-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  /* RTL Mobile Layout */
  [dir="rtl"] .navigation {
    flex-direction: column;
  }
  
  [dir="rtl"] .nav-brand {
    order: 1;
  }
  
  [dir="rtl"] .nav-links {
    order: 2;
  }
  
  [dir="rtl"] .nav-user {
    order: 3;
  }
  
  [dir="rtl"] .nav-brand h2 {
    text-align: center;
  }
}

@media (max-width: 480px) {
  .nav-links {
    flex-direction: column;
    width: 100%;
  }
  
  .nav-link {
    width: 100%;
    text-align: center;
  }
  
  .nav-user {
    flex-direction: column;
    width: 100%;
  }
  
  .user-name,
  .switch-association-btn,
  .logout-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
