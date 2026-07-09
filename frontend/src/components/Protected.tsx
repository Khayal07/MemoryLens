import { Navigate } from "react-router-dom";
import { useAuth } from "../features/auth/AuthContext";
import type { ReactNode } from "react";
import Spinner from "./ui/Spinner";

export default function Protected({
  children,
  to = "/login",
}: {
  children: ReactNode;
  to?: string;
}) {
  const { isAuthenticated, ready } = useAuth();
  if (!ready)
    return (
      <div className="flex justify-center py-16 text-muted">
        <Spinner />
      </div>
    );
  if (!isAuthenticated) return <Navigate to={to} replace />;
  return <>{children}</>;
}
