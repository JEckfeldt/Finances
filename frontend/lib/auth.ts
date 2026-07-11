const TOKEN_KEY = "finance_auth_token";
const EMAIL_KEY = "finance_auth_email";

/**
 * Temporary client-side auth storage.
 * Auth hardening will migrate tokens to httpOnly Secure cookies set by the backend.
 */
export function setAuth(token: string, email: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(EMAIL_KEY, email);
}

export function getToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(TOKEN_KEY);
}

export function getEmail(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(EMAIL_KEY);
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}
