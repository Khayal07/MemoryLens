import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import { az } from "./az";
import { en } from "./en";

export type Lang = "en" | "az";

const DICTS: Record<Lang, Record<string, string>> = { en, az };
const STORAGE_KEY = "memorylens.lang";

/** Saved choice wins; otherwise fall back to the browser language (az → Azerbaijani,
 *  everything else → English). */
function detectLang(): Lang {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "en" || saved === "az") return saved;
  } catch {
    /* localStorage may be unavailable */
  }
  return navigator.language?.toLowerCase().startsWith("az") ? "az" : "en";
}

interface I18n {
  lang: Lang;
  setLang: (l: Lang) => void;
  /** Translate a dotted key, with optional `{var}` interpolation. Falls back to the
   *  English string, then the raw key, so a missing translation never blanks the UI. */
  t: (key: string, vars?: Record<string, string | number>) => string;
}

const Ctx = createContext<I18n | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(detectLang);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((l: Lang) => {
    try {
      localStorage.setItem(STORAGE_KEY, l);
    } catch {
      /* ignore */
    }
    setLangState(l);
  }, []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      let s = DICTS[lang][key] ?? en[key] ?? key;
      if (vars) {
        for (const [k, v] of Object.entries(vars)) {
          s = s.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
        }
      }
      return s;
    },
    [lang],
  );

  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useI18n(): I18n {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useI18n must be used within LanguageProvider");
  return ctx;
}

/** A category's display name in the active language, falling back to the API-provided
 *  name for any category we don't have a translation for. */
export function categoryName(
  t: I18n["t"],
  key: string,
  fallback?: string | null,
): string {
  const v = t(`category.name.${key}`);
  return v.startsWith("category.name.") ? fallback || key : v;
}
