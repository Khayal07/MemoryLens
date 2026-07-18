import { AnimatePresence, m } from "framer-motion";
import { Suspense, useEffect, useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/AuthContext";
import { useI18n } from "../i18n/LanguageContext";
import AuroraBackground from "./AuroraBackground";
import PageTransition from "./motion/PageTransition";
import Spinner from "./ui/Spinner";
import { spring } from "./motion/variants";

const navLink =
  "rounded-[10px] px-3 py-2 text-[0.92rem] font-medium text-muted transition-colors " +
  "hover:bg-raised hover:text-ink focus-visible:outline-2 focus-visible:outline-violet-soft";

/** AZ ⇄ EN segmented toggle. */
function LangToggle() {
  const { lang, setLang, t } = useI18n();
  return (
    <div
      role="group"
      aria-label={t("lang.aria")}
      className="glass ml-1 flex items-center rounded-full p-0.5 text-[0.72rem] font-semibold"
    >
      {(["az", "en"] as const).map((code) => (
        <button
          key={code}
          type="button"
          onClick={() => setLang(code)}
          aria-pressed={lang === code}
          className={
            "rounded-full px-2.5 py-1 transition-colors " +
            (lang === code ? "bg-violet/25 text-ink" : "text-muted hover:text-ink")
          }
        >
          {t(`lang.${code}`)}
        </button>
      ))}
    </div>
  );
}

export default function Layout() {
  const { isAuthenticated, signOut } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => setMenuOpen(false), [location.pathname]);

  function navItems(close: () => void) {
    return isAuthenticated ? (
      <>
        <Link to="/collections" className={navLink} onClick={close}>
          {t("nav.collections")}
        </Link>
        <Link to="/history" className={navLink} onClick={close}>
          {t("nav.history")}
        </Link>
        <Link to="/analytics" className={navLink} onClick={close}>
          {t("nav.analytics")}
        </Link>
        <Link to="/constellation" className={navLink} onClick={close}>
          {t("nav.constellation")}
        </Link>
        <Link to="/challenge" className={navLink} onClick={close}>
          {t("nav.daily")}
        </Link>
        <button
          className={navLink + " text-left"}
          onClick={() => {
            close();
            signOut();
            navigate("/");
          }}
        >
          {t("nav.signOut")}
        </button>
        <LangToggle />
      </>
    ) : (
      <>
        <Link to="/login" className={navLink} onClick={close}>
          {t("nav.signIn")}
        </Link>
        <Link to="/register" className={navLink} onClick={close}>
          {t("nav.createAccount")}
        </Link>
        <LangToggle />
      </>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <AuroraBackground />
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50
          focus:rounded-lg focus:bg-raised focus:px-4 focus:py-2 focus:text-ink"
      >
        {t("nav.skip")}
      </a>

      <header className="sticky top-0 z-20 border-b border-glass-line bg-night/85 md:bg-night/40 md:backdrop-blur-xl md:backdrop-saturate-150">
        <div className="mx-auto flex h-16 max-w-[920px] items-center justify-between px-4 sm:px-6">
          <Link
            to="/"
            className="flex items-center gap-2.5 font-display text-[1.1rem] font-bold tracking-[-0.02em]"
            aria-label={t("nav.home")}
          >
            <m.span
              aria-hidden="true"
              whileHover={{ rotate: 90 }}
              transition={spring}
              className="relative inline-block size-[22px] rounded-full border-2 border-violet
                shadow-[0_0_0_3px_rgba(124,107,245,0.15)]
                after:absolute after:inset-1 after:rounded-full
                after:bg-[radial-gradient(circle_at_35%_30%,var(--color-amber),var(--color-violet))]"
            />
            MemoryLens
          </Link>

          <nav className="hidden items-center gap-1.5 md:flex">{navItems(() => {})}</nav>

          <button
            type="button"
            className="rounded-[10px] p-2 text-muted transition-colors hover:bg-raised hover:text-ink
              focus-visible:outline-2 focus-visible:outline-violet-soft md:hidden"
            aria-expanded={menuOpen}
            aria-controls="mobile-nav"
            aria-label={t("nav.menu")}
            onClick={() => setMenuOpen((o) => !o)}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              {menuOpen ? (
                <path
                  d="M5 5l10 10M15 5L5 15"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              ) : (
                <path
                  d="M3 5.5h14M3 10h14M3 14.5h14"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              )}
            </svg>
          </button>
        </div>

        {menuOpen && (
          <m.nav
            id="mobile-nav"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.15 }}
            className="flex flex-col gap-1 border-t border-glass-line px-4 py-3 md:hidden"
          >
            {navItems(() => setMenuOpen(false))}
          </m.nav>
        )}
      </header>

      <main id="main" className="flex-1 py-12 md:py-12">
        <div className="mx-auto max-w-[920px] px-6">
          <Suspense
            fallback={
              <div className="flex justify-center py-16 text-muted">
                <Spinner />
              </div>
            }
          >
            <AnimatePresence mode="wait">
              <PageTransition key={location.pathname}>
                <Outlet />
              </PageTransition>
            </AnimatePresence>
          </Suspense>
        </div>
      </main>
    </div>
  );
}
