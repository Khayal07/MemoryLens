import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useAuth } from "../features/auth/AuthContext";
import { useI18n } from "../i18n/LanguageContext";
import { api } from "../lib/api";

interface Props {
  searchId: number;
}

/** Mints a public share link for the current (owned) search and copies it to the
 *  clipboard. Only shown to the signed-in owner — sharing requires auth. */
export default function ShareButton({ searchId }: Props) {
  const { isAuthenticated } = useAuth();
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);

  const share = useMutation({
    mutationFn: () => api.createShare(searchId),
    onSuccess: async ({ token }) => {
      const url = `${window.location.origin}/s/${token}`;
      try {
        await navigator.clipboard.writeText(url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      } catch {
        window.prompt(t("share.prompt"), url);
      }
    },
  });

  if (!isAuthenticated || searchId <= 0) return null;

  return (
    <button
      type="button"
      onClick={() => share.mutate()}
      disabled={share.isPending}
      className="glass inline-flex items-center gap-2 rounded-full px-4 py-2 text-[0.85rem]
        font-medium text-muted transition-colors hover:border-violet/40 hover:text-ink
        focus-visible:outline-2 focus-visible:outline-violet-soft disabled:opacity-50"
    >
      <span aria-hidden="true">↗</span>
      {copied ? t("share.copied") : share.isPending ? t("share.creating") : t("share.share")}
    </button>
  );
}
