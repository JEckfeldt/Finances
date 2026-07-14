/**
 * Client-side auth helpers. Session is maintained via httpOnly cookies set by the backend.
 */
export function clearAuth(): void {
  // No JWT or sensitive auth state is stored client-side.
}
