'use client';

import { useRef, useState } from 'react';
import { ExamReportView } from '@/components/question-analysis/ExamReportView';
import { useExamAnalysis } from '@/hooks/useExamAnalysis';

/** Question Analysis module: upload exam file and display AI weakness report. */
export function QuestionAnalysisPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { report, extractedPreview, isAnalyzing, error, analyzeFile, reset } =
    useExamAnalysis();

  return (
    <div className="bg-white shadow rounded-xl p-6 space-y-4">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,image/jpeg,image/png,image/webp"
        className="block w-full border rounded-lg p-2"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null;
          setSelectedFile(file);
          reset();
        }}
      />

      <button
        type="button"
        disabled={!selectedFile || isAnalyzing}
        onClick={async () => {
          if (!selectedFile) {
            return;
          }
          await analyzeFile(selectedFile);
        }}
        className="w-full bg-black text-white rounded-lg px-4 py-2 disabled:opacity-50"
      >
        {isAnalyzing ? 'Analyzing…' : 'Analyze Test Paper'}
      </button>

      {error && (
        <p className="text-red-600 text-sm" role="alert">
          {error}
        </p>
      )}

      {extractedPreview && (
        <div className="bg-white border rounded-xl p-4 mt-4">
          <h3 className="font-bold mb-2">Extracted Content Preview</h3>
          <pre className="whitespace-pre-wrap text-sm text-gray-700 overflow-auto max-h-64">
            {extractedPreview}
          </pre>
        </div>
      )}

      {report && <ExamReportView report={report} />}
    </div>
  );
}
