import { m } from "framer-motion";
import { useState, type ReactNode } from "react";
import Alert from "../../components/ui/Alert";
import Button from "../../components/ui/Button";
import Field from "../../components/ui/Field";
import { developIn } from "../../components/motion/variants";
import { useI18n } from "../../i18n/LanguageContext";

interface Props {
  title: string;
  subtitle: string;
  submitLabel: string;
  busyLabel: string;
  passwordAutoComplete: "current-password" | "new-password";
  footer: ReactNode;
  onSubmit: (email: string, password: string) => Promise<void>;
  /** Return an error string to block submit, or null to proceed. */
  validate?: (email: string, password: string) => string | null;
}

/** Shared auth panel used by both Login and Register — the only difference is
 *  copy, autocomplete, footer and optional client-side validation. */
export default function AuthForm({
  title,
  subtitle,
  submitLabel,
  busyLabel,
  passwordAutoComplete,
  footer,
  onSubmit,
  validate,
}: Props) {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handle(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const invalid = validate?.(email, password);
    if (invalid) {
      setError(invalid);
      return;
    }
    setBusy(true);
    try {
      await onSubmit(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.genericError"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <m.form
      variants={developIn}
      initial="hidden"
      animate="show"
      onSubmit={handle}
      className="glass-strong mx-auto max-w-[400px] rounded-lens-lg p-8"
    >
      <h2 className="mb-1.5 font-display text-[1.6rem] font-bold tracking-[-0.02em]">{title}</h2>
      <p className="mb-[22px] text-[0.92rem] text-muted">{subtitle}</p>

      {error && <Alert>{error}</Alert>}

      <Field
        label={t("auth.field.email")}
        type="email"
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <Field
        label={t("auth.field.password")}
        type="password"
        autoComplete={passwordAutoComplete}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <Button type="submit" block disabled={busy}>
        {busy ? busyLabel : submitLabel}
      </Button>

      <p className="mt-[18px] text-center text-[0.88rem] text-muted [&_a]:text-violet-soft [&_a:hover]:underline">
        {footer}
      </p>
    </m.form>
  );
}
