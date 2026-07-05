import type { ReactNode } from "react";

/** Centred empty/zero-data state with an aperture mark and optional action. */
export default function EmptyState({
  title,
  hint,
  action,
}: {
  title: ReactNode;
  hint?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-center">
      <span
        aria-hidden="true"
        className="relative mb-1 inline-block size-9 rounded-full border-2 border-violet/50
          shadow-[0_0_0_4px_rgba(124,107,245,0.12)] after:absolute after:inset-1.5
          after:rounded-full after:bg-[radial-gradient(circle_at_35%_30%,var(--color-amber),var(--color-violet))]"
      />
      <p className="text-ink">{title}</p>
      {hint && <p className="max-w-sm text-[0.9rem] text-muted">{hint}</p>}
      {action}
    </div>
  );
}
