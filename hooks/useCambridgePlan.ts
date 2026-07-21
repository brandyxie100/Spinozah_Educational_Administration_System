'use client';

import React from 'react';
import type {
  CambridgeCurriculum,
  CambridgeTeachingPlan,
} from '@/lib/ai-analysis';
import { ApiError, apiRequest } from '@/lib/api';

export interface GenerateCambridgePlanRequest {
  weaknesses: string[];
  curriculum: CambridgeCurriculum;
  subject: string;
  studentName?: string;
}

interface UseCambridgePlanResult {
  plan: CambridgeTeachingPlan | null;
  isGenerating: boolean;
  error: string | null;
  generatePlan: (input: GenerateCambridgePlanRequest) => Promise<void>;
  reset: () => void;
}

/**
 * Client hook for Cambridge teaching plan generation from weaknesses.
 */
export function useCambridgePlan(): UseCambridgePlanResult {
  const [plan, setPlan] = React.useState<CambridgeTeachingPlan | null>(null);
  const [isGenerating, setIsGenerating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const reset = React.useCallback(() => {
    setPlan(null);
    setError(null);
    setIsGenerating(false);
  }, []);

  const generatePlan = React.useCallback(
    async (input: GenerateCambridgePlanRequest) => {
      setIsGenerating(true);
      setError(null);
      setPlan(null);

      try {
        const teachingPlan = await apiRequest<CambridgeTeachingPlan>(
          '/api/ai/plans/generate',
          {
            method: 'POST',
            body: JSON.stringify(input),
          },
        );
        setPlan(teachingPlan);
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : 'Failed to generate Cambridge plan';
        setError(message);
      } finally {
        setIsGenerating(false);
      }
    },
    [],
  );

  return {
    plan,
    isGenerating,
    error,
    generatePlan,
    reset,
  };
}
