import { Link, useNavigate } from "react-router-dom";
import AuthForm from "../features/auth/AuthForm";
import { useAuth } from "../features/auth/AuthContext";
import { useI18n } from "../i18n/LanguageContext";
import { api, ApiError } from "../lib/api";

export default function Login() {
  const { signIn } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();

  return (
    <AuthForm
      title={t("auth.login.title")}
      subtitle={t("auth.login.subtitle")}
      submitLabel={t("auth.login.submit")}
      busyLabel={t("auth.login.busy")}
      passwordAutoComplete="current-password"
      onSubmit={async (email, password) => {
        try {
          const tokens = await api.login(email, password);
          await signIn(tokens);
          navigate("/");
        } catch (err) {
          throw new Error(err instanceof ApiError ? err.message : t("auth.login.failed"));
        }
      }}
      footer={
        <>
          {t("auth.login.footerPre")} <Link to="/register">{t("auth.login.footerLink")}</Link>
        </>
      }
    />
  );
}
