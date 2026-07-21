import { z } from 'zod';

/** Qualification systems accepted for pathway input (AIJOB-53). */
export const pathwayQualificationSchema = z.enum(['IGCSE', 'A-Level']);

export type PathwayQualification = z.infer<typeof pathwayQualificationSchema>;

/** University regions supported by Skill J. */
export const pathwayRegionSchema = z.enum([
  'UK',
  'USA',
  'Australia',
  'New Zealand',
]);

export type PathwayRegion = z.infer<typeof pathwayRegionSchema>;

/** One subject grade from IGCSE or A-Level results. */
export const subjectGradeSchema = z.object({
  subject: z.string().min(1),
  grade: z.string().min(1),
});

export type SubjectGrade = z.infer<typeof subjectGradeSchema>;

/** Ranked university recommendation. */
export const rankedUniversitySchema = z.object({
  rank: z.number().int().min(1),
  name: z.string(),
  region: pathwayRegionSchema,
  admissionProbability: z.number().min(0).max(100),
  rationale: z.string(),
});

/** Ranked major / course recommendation. */
export const rankedMajorSchema = z.object({
  rank: z.number().int().min(1),
  name: z.string(),
  relatedSubjects: z.array(z.string()),
  admissionProbability: z.number().min(0).max(100),
  rationale: z.string(),
});

/**
 * Structured university pathway recommendation (Skill J / AIJOB-53).
 *
 * Parent-facing output: ranked universities and majors from exam results.
 */
export const pathwayRecommendationSchema = z.object({
  studentName: z.string(),
  qualification: pathwayQualificationSchema,
  grades: z.array(subjectGradeSchema).min(1),
  summary: z.string(),
  universities: z.array(rankedUniversitySchema).min(1),
  majors: z.array(rankedMajorSchema).min(1),
  roadmapSteps: z.array(z.string()),
});

export type RankedUniversity = z.infer<typeof rankedUniversitySchema>;
export type RankedMajor = z.infer<typeof rankedMajorSchema>;
export type PathwayRecommendation = z.infer<typeof pathwayRecommendationSchema>;

/**
 * Parse and validate a pathway recommendation payload.
 *
 * @param data - Raw JSON from OpenAI or API response.
 * @returns Validated pathway recommendation.
 */
export function parsePathwayRecommendation(data: unknown): PathwayRecommendation {
  return pathwayRecommendationSchema.parse(data);
}
