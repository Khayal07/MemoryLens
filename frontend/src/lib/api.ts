import type {
  Category,
  Collection,
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

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const tokens = getTokens();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (tokens) headers.Authorization = `Bearer ${tokens.access_token}`;

  const resp = await fetch(`${BASE}${path}`, { ...options, headers });
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
};
