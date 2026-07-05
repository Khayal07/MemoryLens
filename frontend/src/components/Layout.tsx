import { AnimatePresence, m } from "framer-motion";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/AuthContext";
import PageTransition from "./motion/PageTransition";
import { spring } from "./motion/variants";

const navLink =
  "rounded-[10px] px-3 py-2 text-[0.92rem] font-medium text-muted transition-colors " +
  "hover:bg-raised hover:text-ink focus-visible:outline-2 focus-visible:outline-violet-soft";

export default function Layout() {
  const { isAuthenticated, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50
          focus:rounded-lg focus:bg-raised focus:px-4 focus:py-2 focus:text-ink"
      >
        Skip to content
      </a>

      <header className="sticky top-0 z-20 border-b border-line bg-night/70 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-[920px] items-center justify-between px-6">
          <Link
            to="/"
            className="flex items-center gap-2.5 font-display text-[1.1rem] font-bold tracking-[-0.02em]"
            aria-label="MemoryLens home"
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

          <nav className="flex items-center gap-1.5">
            {isAuthenticated ? (
              <>
                <Link to="/history" className={navLink}>
                  History
                </Link>
                <button
                  className={navLink}
                  onClick={() => {
                    signOut();
                    navigate("/");
                  }}
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className={navLink}>
                  Sign in
                </Link>
                <Link to="/register" className={navLink}>
                  Create account
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main id="main" className="flex-1 py-12 md:py-12">
        <div className="mx-auto max-w-[920px] px-6">
          <AnimatePresence mode="wait">
            <PageTransition key={location.pathname}>
              <Outlet />
            </PageTransition>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
