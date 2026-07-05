import { m } from "framer-motion";
import { cn } from "../../lib/cn";

/** Aperture-style spinner: a violet ring with one bright arc, always turning. */
export default function Spinner({ className }: { className?: string }) {
  return (
    <m.span
      role="status"
      aria-label="Loading"
      className={cn(
        "inline-block size-5 rounded-full border-2 border-line-strong border-t-violet-soft",
        className,
      )}
      animate={{ rotate: 360 }}
      transition={{ repeat: Infinity, ease: "linear", duration: 0.8 }}
    />
  );
}
