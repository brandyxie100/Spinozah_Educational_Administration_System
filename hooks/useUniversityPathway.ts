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
  error: string | null;
  generatePathway: (input: GenerateUniversityPathwayRequest) => Promise<void>;
  reset: () => void;
}

/**
 * Client hook for university pathway recommendations from exam grades.
 */
export function useUniversityPathway(): UseUniversityPathwayResult {
  const [recommendation, setRecommendation] =
    React.useState<PathwayRecommendation | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const reset = React.useCallback(() => {
    setRecommendation(null);
    setError(null);
    setIsGenerating(false);
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

  return {
    recommendation,
    isGenerating,
    error,
    generatePathway,
    reset,
  };
}
