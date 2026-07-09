export type TransactionType = "income" | "expense";

export interface Transaction {
  id: number;
  user_id: number;
  description: string;
  amount: string;
  type: TransactionType;
  category: string;
  transaction_date: string;
  created_at: string;
}

export interface TransactionCreate {
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
  transaction_date: string;
}

export interface TransactionUpdate {
  description: string;
  amount: number;
  type: TransactionType;
  category: string;
  transaction_date: string;
}

export type TransactionSortBy = "date" | "amount" | "category";
export type SortOrder = "asc" | "desc";

export interface TransactionListParams {
  page?: number;
  page_size?: number;
  sort_by?: TransactionSortBy;
  sort_order?: SortOrder;
  search?: string;
  type?: TransactionType;
  category?: string;
}

export interface TransactionListResponse {
  items: Transaction[];
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
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

export interface MonthlySummary {
  income: string;
  expenses: string;
}

export interface DashboardRecentTransaction {
  id: number;
  description: string;
  amount: string;
  type: TransactionType;
  category: string;
  transaction_date: string;
  created_at: string;
}

export interface MonthlySpendingTrend {
  month: string;
  total_expenses: string;
}

export interface MonthlyComparisonTrend {
  month: string;
  income: string;
  expenses: string;
  net_savings: string;
}

export interface DashboardData {
  current_balance: string;
  monthly_summary: MonthlySummary;
  recent_transactions: DashboardRecentTransaction[];
  budget_overview: BudgetProgress[];
  monthly_spending_trend: MonthlySpendingTrend[];
  monthly_comparison_trend: MonthlyComparisonTrend[];
}
