import type { EssayAnalysisReport } from '@/lib/ai-analysis';

interface EssayReportViewProps {
  report: EssayAnalysisReport;
  onDownloadPdf?: () => void;
  isDownloadingPdf?: boolean;
}

/** Renders structured essay scores and rewrite suggestions. */
export function EssayReportView({
  report,
  onDownloadPdf,
  isDownloadingPdf = false,
}: EssayReportViewProps) {
  return (
    <div className="mt-6 space-y-4 rounded-xl bg-slate-100 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-bold">Essay Analysis Report</h2>
        {onDownloadPdf && (
          <button
            type="button"
            onClick={onDownloadPdf}
            disabled={isDownloadingPdf}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {isDownloadingPdf ? 'Preparing PDF…' : 'Download PDF'}
          </button>
        )}
      </div>

      <p>
        <strong>Student:</strong> {report.studentName}
      </p>
      <p>
        <strong>Title:</strong> {report.title}
      </p>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg bg-white p-4">
          <p className="text-sm text-slate-500">Grammar</p>
          <p className="text-2xl font-bold">{report.grammarScore}/100</p>
        </div>
        <div className="rounded-lg bg-white p-4">
          <p className="text-sm text-slate-500">Vocabulary</p>
          <p className="text-2xl font-bold">{report.vocabularyScore}/100</p>
        </div>
        <div className="rounded-lg bg-white p-4">
          <p className="text-sm text-slate-500">Structure</p>
          <p className="text-2xl font-bold">{report.structureScore}/100</p>
        </div>
      </div>

      <p>
        <strong>Summary:</strong> {report.summary}
      </p>

      {report.cohesionNotes.length > 0 && (
        <div>
          <p className="font-semibold">Cohesion</p>
          <ul className="list-disc space-y-1 pl-6">
            {report.cohesionNotes.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {report.suggestions.grammarImprovements.length > 0 && (
        <div>
          <p className="font-semibold">Grammar improvements</p>
          <ul className="list-disc space-y-1 pl-6">
            {report.suggestions.grammarImprovements.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {report.suggestions.advancedVocabulary.length > 0 && (
        <div>
          <p className="font-semibold">Advanced vocabulary</p>
          <ul className="list-disc space-y-1 pl-6">
            {report.suggestions.advancedVocabulary.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {report.suggestions.sentenceRewrites.length > 0 && (
        <div>
          <p className="font-semibold">Sentence rewrites</p>
          <div className="space-y-3 rounded-lg border bg-white p-4">
            {report.suggestions.sentenceRewrites.map((item) => (
              <div key={`${item.original}-${item.rewrite}`}>
                <p className="text-sm text-slate-500">Original</p>
                <p>{item.original}</p>
                <p className="mt-2 text-sm text-slate-500">Rewrite</p>
                <p className="font-medium">{item.rewrite}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <details className="rounded-lg border bg-white p-4">
        <summary className="cursor-pointer font-semibold">Suggestions JSON</summary>
        <pre className="mt-2 overflow-auto text-xs text-slate-700">
          {JSON.stringify(report.suggestions, null, 2)}
        </pre>
      </details>
    </div>
  );
}
