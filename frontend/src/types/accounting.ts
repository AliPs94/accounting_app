export interface Association {
  id: number
  name: string
  created_at: string
  updated_at: string
}

export interface Account {
  id: number
  association: number
  association_name: string
  name: string
  account_type: 'Asset' | 'Liability' | 'Equity' | 'Revenue' | 'Expense'
  parent: number | null
  parent_name: string | null
  code: string
  is_active: boolean
  sub_accounts_count: number
  created_at: string
  updated_at: string
}

export interface VoucherDetail {
  id: number
  account: number
  account_name: string
  account_code: string
  debit: number
  credit: number
  description: string
}

export interface Voucher {
  id: number
  association: number
  association_name: string
  date: string
  description: string
  voucher_type: 'Payment' | 'Receipt' | 'Journal'
  voucher_number: string
  created_by: number
  created_by_username: string
  details: VoucherDetail[]
  total_debits: number
  total_credits: number
  is_balanced: boolean
  created_at: string
  updated_at: string
}

export interface VoucherList {
  id: number
  association_name: string
  date: string
  description: string
  voucher_type: 'Payment' | 'Receipt' | 'Journal'
  voucher_number: string
  created_by_username: string
  total_debits: number
  total_credits: number
  details_count: number
  created_at: string
}

export interface CreateAccountData {
  name: string
  account_type: 'Asset' | 'Liability' | 'Equity' | 'Revenue' | 'Expense'
  parent?: number
  code: string
  is_active?: boolean
}

export interface CreateVoucherData {
  date: string
  description: string
  voucher_type: 'Payment' | 'Receipt' | 'Journal'
  voucher_number: string
  details: Array<{
    account: number
    debit: number
    credit: number
    description?: string
  }>
}

export interface TrialBalanceItem {
  account_code: string
  account_name: string
  account_type: string
  debit: number
  credit: number
}
