import { cn } from "../lib/cn";

interface Props {
  /** Tailwind size classes for the frame, e.g. "w-[148px] h-[214px]". */
  posterSize: string;
  /** Amber for AI-knowledge answers, violet elsewhere. */
  tone?: "violet" | "amber";
  icon?: string | null;
  big?: boolean;
}

/** Aurora aperture — the intentional stand-in when no poster exists (OMDb miss,
 *  songs/actors, or a broken image). A glowing camera-iris ring around the category
 *  icon, tuned to the result's tone, so an empty frame still feels designed. */
export default function PosterPlaceholder({ posterSize, tone = "violet", icon, big }: Props) {
  const amber = tone === "amber";
  return (
    <div
      className={cn(
        "relative flex items-center justify-center overflow-hidden rounded-[10px] border",
        amber
          ? "border-amber/30 bg-[radial-gradient(circle_at_50%_35%,rgba(245,180,104,0.16),rgba(23,26,46,0.55))]"
          : "border-violet/25 bg-[radial-gradient(circle_at_50%_35%,rgba(124,107,245,0.18),rgba(23,26,46,0.55))]",
        posterSize,
      )}
      aria-hidden="true"
    >
      <span
        className={cn(
          "absolute aspect-square w-[82%] rounded-full border",
          amber ? "border-amber/15" : "border-violet/15",
        )}
      />
      <span
        className={cn(
          "absolute aspect-square w-[56%] rounded-full border-2",
          amber
            ? "border-amber/70 shadow-[0_0_22px_-4px_rgba(245,180,104,0.7)]"
            : "border-violet/70 shadow-[0_0_22px_-4px_rgba(124,107,245,0.75)]",
        )}
      />
      <span className={cn("relative opacity-90", big ? "text-[2.1rem]" : "text-[1.5rem]")}>
        {icon ?? "🎞"}
      </span>
    </div>
  );
}
