import type {
  AnalyticsOverview,
  Category,
  ChallengeState,
  Collection,
  ConstellationResponse,
  SearchResponse,
  SearchSummary,
  SimilarItem,
  Tokens,
  User,
} from "./types";

const BASE = "/api/v1";
const TOKEN_KEY = "memorylens.tokens";

export function getTokens(): Tokens | null {
  const raw = localStorage.getItem(TOKEN_KEY);
  return raw ? (JSON.parse(raw) as Tokens) : null;
}

export function setTokens(tokens: Tokens): void {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
}

export function clearTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export const SESSION_EXPIRED_EVENT = "memorylens:session-expired";

// Single-flight refresh: many requests can 401 at once (e.g. a page load fires
// several calls), but we mint exactly one new token pair and share it.
let refreshInFlight: Promise<Tokens | null> | null = null;

function refreshTokens(): Promise<Tokens | null> {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    const refresh_token = getTokens()?.refresh_token;
    if (!refresh_token) {
      return sessionExpired();
    }
    try {
      // Raw fetch — no Authorization header, no recursion back through request().
      const resp = await fetch(`${BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token }),
      });
      if (!resp.ok) return sessionExpired();
      const tokens = (await resp.json()) as Tokens;
      setTokens(tokens);
      return tokens;
    } catch {
      return sessionExpired();
    }
  })();
  return refreshInFlight.finally(() => {
    refreshInFlight = null;
  });
}

function sessionExpired(): null {
  clearTokens();
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
  return null;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const doFetch = (accessToken?: string): Promise<Response> => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    return fetch(`${BASE}${path}`, { ...options, headers });
  };

  let resp = await doFetch(getTokens()?.access_token);

  // An expired access token 401s; transparently refresh once and retry. Skip
  // /auth/* so a bad login/refresh doesn't loop.
  if (
    resp.status === 401 &&
    !path.startsWith("/auth/") &&
    getTokens()?.refresh_token
  ) {
    const refreshed = await refreshTokens();
    if (refreshed) resp = await doFetch(refreshed.access_token);
  }

  if (resp.status === 204) return undefined as T;

  const data = await resp.json().catch(() => null);
  if (!resp.ok) {
    const err = data?.error ?? {};
    throw new ApiError(resp.status, err.code ?? "error", err.message ?? "Something went wrong.");
  }
  return data as T;
}

export const api = {
  categories: () => request<Category[]>("/categories"),

  search: (category: string, query: string) =>
    request<SearchResponse>("/search", {
      method: "POST",
      body: JSON.stringify({ category, query }),
    }),

  register: (email: string, password: string) =>
    request<Tokens>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<Tokens>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>("/auth/me"),

  history: () => request<SearchSummary[]>("/searches"),

  similar: (itemId: number) => request<SimilarItem[]>(`/items/${itemId}/similar`),

  collections: () => request<Collection[]>("/collections"),

  createCollection: (name: string) =>
    request<Collection>("/collections", { method: "POST", body: JSON.stringify({ name }) }),

  renameCollection: (id: number, name: string) =>
    request<Collection>(`/collections/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }),

  deleteCollection: (id: number) =>
    request<void>(`/collections/${id}`, { method: "DELETE" }),

  addToCollection: (id: number, itemId: number) =>
    request<void>(`/collections/${id}/items`, {
      method: "POST",
      body: JSON.stringify({ item_id: itemId }),
    }),

  removeFromCollection: (id: number, itemId: number) =>
    request<void>(`/collections/${id}/items/${itemId}`, { method: "DELETE" }),

  feedback: (searchId: number, itemId: number, vote: 1 | -1) =>
    request<void>("/feedback", {
      method: "POST",
      body: JSON.stringify({ search_id: searchId, item_id: itemId, vote }),
    }),

  createShare: (searchId: number) =>
    request<{ token: string }>(`/searches/${searchId}/share`, { method: "POST" }),

  getShared: (token: string) => request<SearchResponse>(`/share/${token}`),

  analytics: () => request<AnalyticsOverview>("/analytics"),

  constellation: () => request<ConstellationResponse>("/constellation"),

  challengeToday: () => request<ChallengeState>("/challenge/today"),

  challengeGuess: (guess: string) =>
    request<ChallengeState>("/challenge/guess", {
      method: "POST",
      body: JSON.stringify({ guess }),
    }),
};
