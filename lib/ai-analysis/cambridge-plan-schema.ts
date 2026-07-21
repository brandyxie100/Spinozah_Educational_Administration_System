import { z } from 'zod';

/** Cambridge curriculum levels supported by the planner (Skill I). */
export const cambridgeCurriculumSchema = z.enum([
  'Cambridge Primary',
  'Lower Secondary',
  'Checkpoint',
  'IGCSE',
  'AS Level',
  'A Level',
]);

export type CambridgeCurriculum = z.infer<typeof cambridgeCurriculumSchema>;

/** One lesson in a Cambridge teaching plan. */
export const cambridgeLessonSchema = z.object({
  lessonNumber: z.number().int().min(1).max(20),
  title: z.string(),
  objectives: z.array(z.string()),
  activities: z.array(z.string()),
  homework: z.string(),
  addressesWeaknesses: z.array(z.string()),
});

/**
 * Structured Cambridge teaching plan (Skill I / AIJOB-54).
 *
 * Generated from student weaknesses; typically ~10 lessons.
 */
export const cambridgeTeachingPlanSchema = z.object({
  studentName: z.string(),
  curriculum: cambridgeCurriculumSchema,
  subject: z.string(),
  weaknesses: z.array(z.string()).min(1),
  focusTopics: z.array(z.string()),
  summary: z.string(),
  lessons: z.array(cambridgeLessonSchema).min(1).max(20),
});

export type CambridgeLesson = z.infer<typeof cambridgeLessonSchema>;
export type CambridgeTeachingPlan = z.infer<typeof cambridgeTeachingPlanSchema>;

/**
 * Parse and validate a Cambridge teaching plan payload.
 *
 * @param data - Raw JSON from OpenAI or API response.
 * @returns Validated teaching plan.
 */
export function parseCambridgeTeachingPlan(data: unknown): CambridgeTeachingPlan {
  return cambridgeTeachingPlanSchema.parse(data);
}
