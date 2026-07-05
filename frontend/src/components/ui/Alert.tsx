import type { ReactNode } from "react";
import { cn } from "../../lib/cn";

type Tone = "danger" | "info";

const tones: Record<Tone, string> = {
  danger: "border-danger/40 bg-danger/10 text-[#ffc2cd]",
  info: "border-violet/40 bg-violet/10 text-ink",
};

/** Inline status message for form and load errors. */
export default function Alert({
  tone = "danger",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "mb-4 rounded-[11px] border px-3.5 py-3 text-[0.88rem]",
        tones[tone],
        className,
      )}
    >
      {children}
    </div>
  );
}
