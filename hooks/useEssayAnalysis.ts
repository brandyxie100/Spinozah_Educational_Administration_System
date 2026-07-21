'use client';

import React from 'react';
import type { EssayAnalysisReport } from '@/lib/ai-analysis';
import { ApiError, apiRequest } from '@/lib/api';

interface UseEssayAnalysisResult {
  report: EssayAnalysisReport | null;
  extractedPreview: string;
  isAnalyzing: boolean;
  isDownloadingPdf: boolean;
  error: string | null;
  analyzeText: (text: string, studentName?: string) => Promise<void>;
  analyzeFile: (file: File) => Promise<void>;
  downloadPdf: () => Promise<void>;
  reset: () => void;
}

/**
 * Client hook for essay analysis (paste or upload) and optional PDF download.
 */
export function useEssayAnalysis(): UseEssayAnalysisResult {
  const [report, setReport] = React.useState<EssayAnalysisReport | null>(null);
  const [extractedPreview, setExtractedPreview] = React.useState('');
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const reset = React.useCallback(() => {
    setReport(null);
    setExtractedPreview('');
    setError(null);
    setIsAnalyzing(false);
    setIsDownloadingPdf(false);
  }, []);

  const analyzeText = React.useCallback(async (text: string, studentName?: string) => {
    setIsAnalyzing(true);
    setError(null);
    setReport(null);

    try {
      const analysisReport = await apiRequest<EssayAnalysisReport>(
        '/api/ai/essays/analyze',
        {
          method: 'POST',
          body: JSON.stringify({ text, studentName }),
        },
      );
      setReport(analysisReport);
      setExtractedPreview(analysisReport.extractedTextPreview);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : 'Failed to analyze essay';
      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const analyzeFile = React.useCallback(async (file: File) => {
    setIsAnalyzing(true);
    setError(null);
    setReport(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const analysisReport = await apiRequest<EssayAnalysisReport>(
        '/api/ai/essays/analyze',
        {
          method: 'POST',
          body: formData,
        },
      );
      setReport(analysisReport);
      setExtractedPreview(analysisReport.extractedTextPreview);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : 'Failed to analyze essay';
      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const downloadPdf = React.useCallback(async () => {
    if (!report) {
      return;
    }
    setIsDownloadingPdf(true);
    setError(null);
    try {
      const response = await fetch('/api/ai/essays/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report),
      });
      if (!response.ok) {
        const body = (await response.json().catch(() => null)) as {
          error?: string;
        } | null;
        throw new Error(body?.error ?? 'Failed to download PDF');
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'essay-analysis.pdf';
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download PDF');
    } finally {
      setIsDownloadingPdf(false);
    }
  }, [report]);

  return {
    report,
    extractedPreview,
    isAnalyzing,
    isDownloadingPdf,
    error,
    analyzeText,
    analyzeFile,
    downloadPdf,
    reset,
  };
}
