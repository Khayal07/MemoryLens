import { Link, useNavigate } from "react-router-dom";
import AuthForm from "../features/auth/AuthForm";
import { useAuth } from "../features/auth/AuthContext";
import { api, ApiError } from "../lib/api";

export default function Login() {
  const { signIn } = useAuth();
  const navigate = useNavigate();

  return (
    <AuthForm
      title="Welcome back"
      subtitle="Sign in to keep your search history."
      submitLabel="Sign in"
      busyLabel="Signing in…"
      passwordAutoComplete="current-password"
      onSubmit={async (email, password) => {
        try {
          const tokens = await api.login(email, password);
          await signIn(tokens);
          navigate("/");
        } catch (err) {
          throw new Error(err instanceof ApiError ? err.message : "Sign in failed.");
        }
      }}
      footer={
        <>
          New here? <Link to="/register">Create an account</Link>
        </>
      }
    />
  );
}
