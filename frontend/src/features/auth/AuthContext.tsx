import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, clearTokens, getTokens, setTokens } from "../../lib/api";
import type { Tokens, User } from "../../lib/types";

interface AuthState {
  user: User | null;
  ready: boolean;
  isAuthenticated: boolean;
  signIn: (tokens: Tokens) => Promise<void>;
  signOut: () => void;
}

const AuthCtx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  async function load() {
    if (!getTokens()) {
      setUser(null);
      setReady(true);
      return;
    }
    try {
      setUser(await api.me());
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setReady(true);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function signIn(tokens: Tokens) {
    setTokens(tokens);
    setUser(await api.me());
  }

  function signOut() {
    clearTokens();
    setUser(null);
  }

  return (
    <AuthCtx.Provider
      value={{ user, ready, isAuthenticated: !!user, signIn, signOut }}
    >
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
