import type { MismatchSuggestion } from "../lib/types";

interface Props {
  suggestion: MismatchSuggestion;
  onSwitch: (category: string) => void;
}

/** A soft nudge — never an automatic redirect. The user stays in control. */
export default function MismatchBanner({ suggestion, onSwitch }: Props) {
  return (
    <div className="mismatch" role="status">
      <p>{suggestion.message}</p>
      <button className="btn btn-ghost" onClick={() => onSwitch(suggestion.suspected_category)}>
        Switch to {suggestion.suspected_category}
      </button>
    </div>
  );
}
