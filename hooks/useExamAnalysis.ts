'use client';

import React from 'react';
import type { ExamAnalysisReport } from '@/lib/ai-analysis';

interface UseExamAnalysisResult {
  report: ExamAnalysisReport | null;
  extractedPreview: string;
  isAnalyzing: boolean;
  error: string | null;
  analyzeFile: (file: File) => Promise<void>;
  reset: () => void;
}

/**
 * Client hook for uploading an exam file and fetching a structured AI report.
 */
export function useExamAnalysis(): UseExamAnalysisResult {
  const [report, setReport] = React.useState<ExamAnalysisReport | null>(null);
  const [extractedPreview, setExtractedPreview] = React.useState('');
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const reset = React.useCallback(() => {
    setReport(null);
    setExtractedPreview('');
    setError(null);
    setIsAnalyzing(false);
  }, []);

  const analyzeFile = React.useCallback(async (file: File) => {
    setIsAnalyzing(true);
    setError(null);
    setReport(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/ai/exams/analyze', {
        method: 'POST',
        body: formData,
      });

      const payload: ExamAnalysisReport | { error?: string } =
        await response.json();

      if (!response.ok) {
        const message =
          'error' in payload && payload.error
            ? payload.error
            : 'Failed to analyze exam';
        throw new Error(message);
      }

      const analysisReport = payload as ExamAnalysisReport;
      setReport(analysisReport);
      setExtractedPreview(analysisReport.extractedTextPreview);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to analyze exam';
      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  return {
    report,
    extractedPreview,
    isAnalyzing,
    error,
    analyzeFile,
    reset,
  };
}
