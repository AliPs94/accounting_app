export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  association: string
  association_id: number
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  association_id: number
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface AuthResponse {
  user: User
  tokens: AuthTokens
}

export interface LoginResponse {
  user: User
  tokens: AuthTokens
}

