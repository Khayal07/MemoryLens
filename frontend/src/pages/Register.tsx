import { Link, useNavigate } from "react-router-dom";
import AuthForm from "../features/auth/AuthForm";
import { useAuth } from "../features/auth/AuthContext";
import { api, ApiError } from "../lib/api";

export default function Register() {
  const { signIn } = useAuth();
  const navigate = useNavigate();

  return (
    <AuthForm
      title="Create account"
      subtitle="Save every search and pick up where you left off."
      submitLabel="Create account"
      busyLabel="Creating…"
      passwordAutoComplete="new-password"
      validate={(_email, password) =>
        password.length < 8 ? "Password must be at least 8 characters." : null
      }
      onSubmit={async (email, password) => {
        try {
          const tokens = await api.register(email, password);
          await signIn(tokens);
          navigate("/");
        } catch (err) {
          throw new Error(err instanceof ApiError ? err.message : "Could not create account.");
        }
      }}
      footer={
        <>
          Already have one? <Link to="/login">Sign in</Link>
        </>
      }
    />
  );
}
