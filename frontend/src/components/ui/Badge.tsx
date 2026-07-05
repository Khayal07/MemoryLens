import type { ReactNode } from "react";
import { cn } from "../../lib/cn";

type Tone = "amber" | "violet" | "neutral";

const tones: Record<Tone, string> = {
  amber: "text-amber border-amber/40 bg-amber/10",
  violet: "text-violet-soft border-violet/40 bg-violet/10",
  neutral: "text-muted border-line bg-white/[0.03]",
};

/** Small pill label — used for the "AI knowledge" marker and category chips. */
export default function Badge({
  tone = "neutral",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1",
        "font-mono text-[0.68rem] uppercase tracking-[0.08em]",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
