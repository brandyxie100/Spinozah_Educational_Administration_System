interface BackButtonProps {
  onBack: () => void;
}

/** Shared back navigation control for dashboard module views. */
export function BackButton({ onBack }: BackButtonProps) {
  return (
    <button
      type="button"
      onClick={onBack}
      className="mb-6 bg-black text-white px-4 py-2 rounded-lg"
    >
      ← Back
    </button>
  );
}
