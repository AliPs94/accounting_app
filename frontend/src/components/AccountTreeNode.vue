<template>
  <div class="account-tree-node">
    <div class="account-item" :style="{ paddingLeft: `${level * 20 + 10}px` }">
      <div class="account-info">
        <span class="account-code">{{ account.code }}</span>
        <span class="account-name">{{ account.name }}</span>
        <span :class="`account-type-badge ${account.account_type.toLowerCase()}`">
          {{ account.account_type }}
        </span>
        <span :class="`status-badge ${account.is_active ? 'active' : 'inactive'}`">
          {{ account.is_active ? 'Active' : 'Inactive' }}
        </span>
      </div>
      <div class="account-actions">
        <button @click="$emit('edit', account)" class="btn-edit">Edit</button>
        <button @click="$emit('delete', account)" class="btn-delete">Delete</button>
      </div>
    </div>
    
    <!-- Render sub-accounts if any -->
    <div v-if="account.sub_accounts && account.sub_accounts.length > 0" class="sub-accounts">
      <AccountTreeNode
        v-for="subAccount in account.sub_accounts"
        :key="subAccount.id"
        :account="subAccount"
        :level="level + 1"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Account } from '@/types/accounting'

interface Props {
  account: Account & { sub_accounts?: Account[] }
  level: number
}

defineProps<Props>()

defineEmits<{
  edit: [account: Account]
  delete: [account: Account]
}>()
</script>

<style scoped>
.account-tree-node {
  margin-bottom: 5px;
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.account-item:hover {
  background-color: #f8f9fa;
}

.account-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.account-code {
  font-weight: 600;
  color: #333;
  min-width: 60px;
}

.account-name {
  color: #555;
  flex: 1;
}

.account-type-badge {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.account-type-badge.asset { background: #d4edda; color: #155724; }
.account-type-badge.liability { background: #f8d7da; color: #721c24; }
.account-type-badge.equity { background: #d1ecf1; color: #0c5460; }
.account-type-badge.revenue { background: #d4edda; color: #155724; }
.account-type-badge.expense { background: #fff3cd; color: #856404; }

.status-badge {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.active { background: #d4edda; color: #155724; }
.status-badge.inactive { background: #f8d7da; color: #721c24; }

.account-actions {
  display: flex;
  gap: 5px;
}

.btn-edit, .btn-delete {
  padding: 4px 8px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s;
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

.sub-accounts {
  margin-left: 20px;
}
</style>
