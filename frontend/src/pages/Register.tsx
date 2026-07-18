import { Link, useNavigate } from "react-router-dom";
import AuthForm from "../features/auth/AuthForm";
import { useAuth } from "../features/auth/AuthContext";
import { useI18n } from "../i18n/LanguageContext";
import { api, ApiError } from "../lib/api";

export default function Register() {
  const { signIn } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();

  return (
    <AuthForm
      title={t("auth.register.title")}
      subtitle={t("auth.register.subtitle")}
      submitLabel={t("auth.register.submit")}
      busyLabel={t("auth.register.busy")}
      passwordAutoComplete="new-password"
      validate={(_email, password) =>
        password.length < 8 ? t("auth.register.short") : null
      }
      onSubmit={async (email, password) => {
        try {
          const tokens = await api.register(email, password);
          await signIn(tokens);
          navigate("/");
        } catch (err) {
          throw new Error(err instanceof ApiError ? err.message : t("auth.register.failed"));
        }
      }}
      footer={
        <>
          {t("auth.register.footerPre")} <Link to="/login">{t("auth.register.footerLink")}</Link>
        </>
      }
    />
  );
}
