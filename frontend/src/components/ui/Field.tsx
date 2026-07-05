import type { InputHTMLAttributes } from "react";
import { useId } from "react";
import { cn } from "../../lib/cn";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

/** Labelled text input. Generates a stable id so the label is associated. */
export default function Field({ label, className, id, ...props }: Props) {
  const auto = useId();
  const inputId = id ?? auto;
  return (
    <div className="mb-4">
      <label htmlFor={inputId} className="mb-1.5 block text-[0.82rem] text-muted">
        {label}
      </label>
      <input
        id={inputId}
        className={cn(
          "w-full rounded-[11px] border border-line-strong bg-night px-3.5 py-3 text-ink",
          "text-[0.98rem] transition-[box-shadow,border-color] placeholder:text-faint",
          "focus:border-violet focus:outline-none focus:ring-[3px] focus:ring-violet/20",
          className,
        )}
        {...props}
      />
    </div>
  );
}
