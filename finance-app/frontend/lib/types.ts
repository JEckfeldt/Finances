export type TransactionType = "income" | "expense";

export interface Transaction {
  id: number;
  user_id: number;
  description: string;
  amount: string;
  type: TransactionType;
  category: string;
  created_at: string;
}

export interface TransactionCreate {
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
}

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Budget {
  id: number;
  user_id: number;
  category: string;
  limit_amount: string;
  created_at: string;
  updated_at: string;
}

export interface BudgetCreate {
  category: string;
  limit_amount: number;
}

export interface BudgetUpdate {
  category: string;
  limit_amount: number;
}

export interface BudgetProgress {
  category: string;
  limit_amount: string;
  spent: string;
  remaining: string;
  percentage: number;
}

export interface BudgetWithProgress extends Budget {
  spent: string;
  remaining: string;
  percentage: number;
}
