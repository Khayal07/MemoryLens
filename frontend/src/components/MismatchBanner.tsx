import { m } from "framer-motion";
import type { MismatchSuggestion } from "../lib/types";
import { useI18n } from "../i18n/LanguageContext";
import Button from "./ui/Button";
import { fadeUp } from "./motion/variants";

interface Props {
  suggestion: MismatchSuggestion;
  onSwitch: (category: string) => void;
}

/** A soft nudge — never an automatic redirect. The user stays in control. */
export default function MismatchBanner({ suggestion, onSwitch }: Props) {
  const { t } = useI18n();
  return (
    <m.div
      variants={fadeUp}
      initial="hidden"
      animate="show"
      role="status"
      className="my-[18px] flex items-center justify-between gap-3.5 rounded-lens border
        border-amber/35 bg-gradient-to-b from-amber/10 to-amber/5 px-4 py-3.5"
    >
      <p className="m-0 text-[0.92rem]">
        {suggestion.message?.trim() ||
          t("mismatch.looksLike", { category: suggestion.suspected_category })}
      </p>
      <Button variant="ghost" onClick={() => onSwitch(suggestion.suspected_category)}>
        {t("mismatch.switchTo", { category: suggestion.suspected_category })}
      </Button>
    </m.div>
  );
}
