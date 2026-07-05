import { cn } from "../../lib/cn";

/** Shimmering placeholder. `animate-shimmer` + the gradient are defined in
 *  index.css so the sweep respects prefers-reduced-motion there. */
export default function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "rounded-lens bg-[linear-gradient(100deg,var(--color-raised)_30%,#20244f_50%,var(--color-raised)_70%)]",
        "bg-[length:200%_100%] animate-shimmer",
        className,
      )}
    />
  );
}
