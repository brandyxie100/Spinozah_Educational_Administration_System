'use client';

import { useRef, useState } from 'react';
import { EssayReportView } from '@/components/essay-analysis/EssayReportView';
import { useEssayAnalysis } from '@/hooks/useEssayAnalysis';

/** AI Reports module: paste or upload an essay for structured AI scoring. */
export function EssayAnalysisPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [essayText, setEssayText] = useState('');
  const [studentName, setStudentName] = useState('');
  const {
    report,
    extractedPreview,
    isAnalyzing,
    isDownloadingPdf,
    error,
    analyzeText,
    analyzeFile,
    downloadPdf,
    reset,
  } = useEssayAnalysis();

  return (
    <div className="space-y-4 rounded-xl bg-white p-6 shadow">
      <label className="block text-sm font-medium text-slate-700">
        Student name (optional)
        <input
          type="text"
          value={studentName}
          onChange={(event) => setStudentName(event.target.value)}
          className="mt-1 block w-full rounded-lg border p-2"
          placeholder="e.g. Charlotte"
        />
      </label>

      <label className="block text-sm font-medium text-slate-700">
        Paste essay text
        <textarea
          value={essayText}
          onChange={(event) => {
            setEssayText(event.target.value);
          }}
          rows={8}
          className="mt-1 block w-full rounded-lg border p-2 font-mono text-sm"
          placeholder="Paste the student essay here…"
        />
      </label>

      <p className="text-center text-sm text-slate-500">— or upload a file —</p>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,image/jpeg,image/png,image/webp"
        className="block w-full rounded-lg border p-2"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null;
          setSelectedFile(file);
          reset();
        }}
      />

      <div className="grid gap-3 sm:grid-cols-2">
        <button
          type="button"
          disabled={!essayText.trim() || isAnalyzing}
          onClick={async () => {
            await analyzeText(essayText, studentName || undefined);
          }}
          className="w-full rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
        >
          {isAnalyzing ? 'Analyzing…' : 'Analyze pasted essay'}
        </button>
        <button
          type="button"
          disabled={!selectedFile || isAnalyzing}
          onClick={async () => {
            if (!selectedFile) {
              return;
            }
            await analyzeFile(selectedFile);
          }}
          className="w-full rounded-lg bg-slate-800 px-4 py-2 text-white disabled:opacity-50"
        >
          {isAnalyzing ? 'Analyzing…' : 'Analyze uploaded file'}
        </button>
      </div>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {extractedPreview && (
        <div className="mt-4 rounded-xl border bg-white p-4">
          <h3 className="mb-2 font-bold">Essay preview</h3>
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap text-sm text-gray-700">
            {extractedPreview}
          </pre>
        </div>
      )}

      {report && (
        <EssayReportView
          report={report}
          onDownloadPdf={downloadPdf}
          isDownloadingPdf={isDownloadingPdf}
        />
      )}
    </div>
  );
}
