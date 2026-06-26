import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/AuthContext";

export default function Layout() {
  const { isAuthenticated, signOut } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="shell">
      <header className="nav">
        <div className="wrap nav-inner">
          <Link to="/" className="brand" aria-label="MemoryLens home">
            <span className="lens" aria-hidden="true" />
            MemoryLens
          </Link>
          <nav className="nav-links">
            {isAuthenticated ? (
              <>
                <Link to="/history" className="nav-link">
                  History
                </Link>
                <button
                  className="nav-link"
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
                <Link to="/login" className="nav-link">
                  Sign in
                </Link>
                <Link to="/register" className="nav-link">
                  Create account
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="main">
        <div className="wrap">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
