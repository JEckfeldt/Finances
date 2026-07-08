import type { Transaction, TransactionCreate } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getTransactions(): Promise<Transaction[]> {
  const response = await fetch(`${API_URL}/transactions`, {
    cache: "no-store",
  });
  return handleResponse<Transaction[]>(response);
}

export async function createTransaction(
  data: TransactionCreate
): Promise<Transaction> {
  const response = await fetch(`${API_URL}/transactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Transaction>(response);
}
