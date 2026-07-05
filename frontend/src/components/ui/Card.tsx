import type { HTMLAttributes } from "react";
import { cn } from "../../lib/cn";

interface Props extends HTMLAttributes<HTMLDivElement> {
  /** Adds the indigo "best match" glow ring. */
  glow?: boolean;
  /** Shifts the glow to amber (AI-knowledge results). */
  amber?: boolean;
}

/** Surface primitive: raised panel with the lens corner radius. */
export default function Card({ glow, amber, className, children, ...props }: Props) {
  return (
    <div
      className={cn(
        "rounded-lens border bg-raised",
        glow
          ? amber
            ? "border-amber/40 shadow-glow-amber ring-1 ring-amber/20"
            : "border-violet/40 shadow-glow ring-1 ring-violet/20"
          : "border-line",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
