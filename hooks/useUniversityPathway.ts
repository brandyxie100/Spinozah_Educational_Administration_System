'use client';

import React from 'react';
import type {
  PathwayQualification,
  PathwayRecommendation,
  SubjectGrade,
} from '@/lib/ai-analysis';
import { ApiError, apiRequest } from '@/lib/api';

export interface GenerateUniversityPathwayRequest {
  grades: SubjectGrade[];
  qualification: PathwayQualification;
  studentName?: string;
}

interface UseUniversityPathwayResult {
  recommendation: PathwayRecommendation | null;
  isGenerating: boolean;
  isDownloadingPdf: boolean;
  error: string | null;
  generatePathway: (input: GenerateUniversityPathwayRequest) => Promise<void>;
  downloadPdf: () => Promise<void>;
  reset: () => void;
}

/**
 * Client hook for university pathway recommendations from exam grades.
 */
export function useUniversityPathway(): UseUniversityPathwayResult {
  const [recommendation, setRecommendation] =
    React.useState<PathwayRecommendation | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const reset = React.useCallback(() => {
    setRecommendation(null);
    setError(null);
    setIsGenerating(false);
    setIsDownloadingPdf(false);
  }, []);

  const generatePathway = React.useCallback(
    async (input: GenerateUniversityPathwayRequest) => {
      setIsGenerating(true);
      setError(null);
      setRecommendation(null);

      try {
        const result = await apiRequest<PathwayRecommendation>(
          '/api/ai/pathway/generate',
          {
            method: 'POST',
            body: JSON.stringify(input),
          },
        );
        setRecommendation(result);
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : 'Failed to generate university pathway';
        setError(message);
      } finally {
        setIsGenerating(false);
      }
    },
    [],
  );

  const downloadPdf = React.useCallback(async () => {
    if (!recommendation) {
      return;
    }
    setIsDownloadingPdf(true);
    setError(null);
    try {
      const response = await fetch('/api/ai/pathway/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recommendation),
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
      anchor.download = 'university-pathway.pdf';
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download PDF');
    } finally {
      setIsDownloadingPdf(false);
    }
  }, [recommendation]);

  return {
    recommendation,
    isGenerating,
    isDownloadingPdf,
    error,
    generatePathway,
    downloadPdf,
    reset,
  };
}
