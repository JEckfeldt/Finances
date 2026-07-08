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
