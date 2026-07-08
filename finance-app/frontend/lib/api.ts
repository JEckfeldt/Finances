import { getToken } from "@/lib/auth";
import type {
  Budget,
  BudgetCreate,
  BudgetProgress,
  BudgetUpdate,
  DashboardData,
  LoginRequest,
  TokenResponse,
  Transaction,
  TransactionCreate,
  TransactionListParams,
  TransactionListResponse,
  TransactionUpdate,
  User,
  UserCreate,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let error = await response.text();
    try {
      const parsed = JSON.parse(error) as { detail?: string };
      if (typeof parsed.detail === "string") {
        error = parsed.detail;
      }
    } catch {
      // Keep raw error text when response is not JSON.
    }
    throw new Error(error || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function authFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();
  if (!token) {
    throw new Error("Not authenticated");
  }

  const headers = new Headers(options.headers);
  headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      searchParams.set(key, String(value));
    }
  }
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export async function register(data: UserCreate): Promise<User> {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<User>(response);
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<TokenResponse>(response);
}

export async function getCurrentUser(): Promise<User> {
  const response = await authFetch("/auth/me");
  return handleResponse<User>(response);
}

export async function getTransactions(
  params: TransactionListParams = {}
): Promise<TransactionListResponse> {
  const query = buildQuery({
    page: params.page,
    page_size: params.page_size,
    sort_by: params.sort_by,
    sort_order: params.sort_order,
    search: params.search,
    type: params.type,
    category: params.category === "all" ? undefined : params.category,
  });
  const response = await authFetch(`/transactions${query}`);
  return handleResponse<TransactionListResponse>(response);
}

export async function getTransactionCategories(): Promise<string[]> {
  const response = await authFetch("/transactions/categories");
  return handleResponse<string[]>(response);
}

export async function createTransaction(
  data: TransactionCreate
): Promise<Transaction> {
  const response = await authFetch("/transactions", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return handleResponse<Transaction>(response);
}

export async function updateTransaction(
  id: number,
  data: TransactionUpdate
): Promise<Transaction> {
  const response = await authFetch(`/transactions/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return handleResponse<Transaction>(response);
}

export async function deleteTransaction(id: number): Promise<void> {
  const response = await authFetch(`/transactions/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    await handleResponse(response);
  }
}

export async function getBudgets(): Promise<Budget[]> {
  const response = await authFetch("/budgets");
  return handleResponse<Budget[]>(response);
}

export async function createBudget(data: BudgetCreate): Promise<Budget> {
  const response = await authFetch("/budgets", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return handleResponse<Budget>(response);
}

export async function updateBudget(
  id: number,
  data: BudgetUpdate
): Promise<Budget> {
  const response = await authFetch(`/budgets/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return handleResponse<Budget>(response);
}

export async function deleteBudget(id: number): Promise<void> {
  const response = await authFetch(`/budgets/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    await handleResponse(response);
  }
}

export async function getBudgetProgress(): Promise<BudgetProgress[]> {
  const response = await authFetch("/budgets/progress");
  return handleResponse<BudgetProgress[]>(response);
}

export async function getDashboard(): Promise<DashboardData> {
  const response = await authFetch("/dashboard");
  return handleResponse<DashboardData>(response);
}
