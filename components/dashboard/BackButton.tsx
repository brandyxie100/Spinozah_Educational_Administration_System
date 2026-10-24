interface BackButtonProps {
  onBack: () => void;
}

/** Soft River back control for module views. */
export function BackButton({ onBack }: BackButtonProps) {
  return (
    <button
      type="button"
      onClick={onBack}
      className="mb-6 rounded-full border border-sp-hairline bg-sp-surface px-4 py-2 text-sm font-medium text-sp-ink transition-colors hover:border-sp-orange hover:bg-sp-orange-soft focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sp-orange"
    >
      ← Back
    </button>
  );
}
