// In-memory auth store. Intentionally NOT localStorage/sessionStorage —
// keeping the access token and user out of persistent browser storage
// reduces what an XSS payload could exfiltrate. This is lost on a full
// page reload by design; rehydrate it on app mount by calling the
// refresh endpoint (it relies on the httpOnly refresh-token cookie).
//
// Plain axios modules (like client.js) can't read React state directly,
// so this small pub/sub store is the shared source of truth for both
// React components and non-React code.

let state = {
  accessToken: null,
  user: null,
};

const listeners = new Set();

export function getAuthState() {
  return state;
}

export function setAuthState(partial) {
  state = { ...state, ...partial };
  listeners.forEach((listener) => listener(state));
}

export function clearAuth() {
  setAuthState({ accessToken: null, user: null });
}

// Optional: lets React components subscribe to changes made outside React
// (e.g. a token refresh triggered by the axios interceptor).
// Usage: const authState = useSyncExternalStore(subscribeAuth, getAuthState);
export function subscribeAuth(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
