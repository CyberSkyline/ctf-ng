import { APIPREFIX, ROUTEPREFIX } from '@/constants';

/**
 * Remembers where to send the user after logging in, across the SSO round trip.
 *
 * The SSO flow leaves the app (backend -> Okta -> backend callback), and the callback always lands on
 * the app root, so the login page's `?redirect=` param is lost. We stash it in sessionStorage before
 * leaving and pick it back up on the next page load once the user is authenticated.
 *
 * sessionStorage (rather than localStorage) keeps the value scoped to the tab that started the login,
 * and it survives the cross-origin redirects since the tab returns to the same origin.
 */
const STORAGE_KEY = 'postLoginRedirect';

// Long enough to get through Okta (including PIV/CAC prompts), short enough that an abandoned
// login doesn't hijack a later, unrelated one.
const MAX_AGE_MS = 15 * 60 * 1000;

/** Whether the path is `prefix` itself or nested under it. An empty prefix contains every path. */
function isUnder(pathname: string, prefix: string) {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

/**
 * Returns the given redirect target if it is a same-origin page of the app, otherwise null.
 * Guards against open redirects via a crafted `?redirect=` param, and keeps it from pointing at
 * backend endpoints (which live under the API prefix) rather than app routes.
 */
export function safeRedirectPath(redirect: string | null | undefined): string | null {
  if (!redirect || !redirect.startsWith('/') || redirect.startsWith('//') || redirect.startsWith('/\\')) {
    return null;
  }

  try {
    // checks run on the parsed pathname so `..` segments and encoding can't slip past the prefix checks
    const url = new URL(redirect, window.location.origin);
    if (url.origin !== window.location.origin || !isUnder(url.pathname, ROUTEPREFIX) || isUnder(url.pathname, APIPREFIX)) {
      return null;
    }
    return url.pathname + url.search + url.hash;
  } catch {
    return null;
  }
}

/**
 * Drops any saved redirect target. Call when logging in without SSO, so a target left over from an
 * abandoned SSO attempt doesn't override where that login sends the user.
 */
export function clearPostLoginRedirect() {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // storage unavailable, so there is nothing saved to clear
  }
}

/** Saves the redirect target before leaving the app for SSO login. Clears any stale target if none is given. */
export function savePostLoginRedirect(redirect: string | null) {
  const path = safeRedirectPath(redirect);

  if (!path) {
    clearPostLoginRedirect();
    return;
  }

  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ path, savedAt : Date.now() }));
  } catch {
    // storage unavailable (e.g. blocked by the browser), fall back to the default post-login page
  }
}

/**
 * If the user is authenticated and a post-login redirect was saved, consumes it and navigates there.
 * Call before rendering the app.
 * @returns true if a navigation was started, in which case the app should not be rendered.
 */
export function resumePostLoginRedirect(): boolean {
  if (!window.init.userId) {
    // not logged in (yet), leave any saved target for after login
    return false;
  }

  let saved: { path?: string, savedAt?: number } | null = null;
  try {
    saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? 'null');
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    return false;
  }

  const path = safeRedirectPath(saved?.path);
  if (!path || !saved?.savedAt || Date.now() - saved.savedAt > MAX_AGE_MS) {
    return false;
  }

  const current = window.location.pathname + window.location.search + window.location.hash;
  if (path === current) {
    return false;
  }

  window.location.replace(path);
  return true;
}
