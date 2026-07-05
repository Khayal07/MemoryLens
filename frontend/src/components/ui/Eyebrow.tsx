import type { ReactNode } from "react";
import { cn } from "../../lib/cn";

/** Mono uppercase label that sits above headings and result sections. */
export default function Eyebrow({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <span
      className={cn(
        "font-mono text-[0.72rem] uppercase tracking-[0.18em] text-faint",
        className,
      )}
    >
      {children}
    </span>
  );
}
