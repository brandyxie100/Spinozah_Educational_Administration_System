/**
 * @jest-environment node
 */
import { parseCambridgeTeachingPlan } from '../cambridge-plan-schema';
import { buildMockCambridgeTeachingPlan } from '../cambridge-plan-prompts';

describe('cambridge-plan-schema', () => {
  it('test_parseCambridgeTeachingPlan_validPayload_returnsPlan', () => {
    const plan = parseCambridgeTeachingPlan({
      studentName: 'Charlotte',
      curriculum: 'IGCSE',
      subject: 'Mathematics',
      weaknesses: ['Fractions'],
      focusTopics: ['Fractions'],
      summary: 'Remediate fractions',
      lessons: [
        {
          lessonNumber: 1,
          title: 'Fractions intro',
          objectives: ['Identify parts of a whole'],
          activities: ['Warm-up quiz'],
          homework: 'Worksheet 1',
          addressesWeaknesses: ['Fractions'],
        },
      ],
    });

    expect(plan.curriculum).toBe('IGCSE');
    expect(plan.lessons).toHaveLength(1);
  });

  it('test_parseCambridgeTeachingPlan_emptyWeaknesses_throws', () => {
    expect(() =>
      parseCambridgeTeachingPlan({
        studentName: 'Charlotte',
        curriculum: 'IGCSE',
        subject: 'Mathematics',
        weaknesses: [],
        focusTopics: [],
        summary: 'x',
        lessons: [
          {
            lessonNumber: 1,
            title: 't',
            objectives: ['o'],
            activities: ['a'],
            homework: 'h',
            addressesWeaknesses: [],
          },
        ],
      }),
    ).toThrow();
  });

  it('test_buildMockCambridgeTeachingPlan_tenLessons_mapsWeaknesses', () => {
    const plan = buildMockCambridgeTeachingPlan({
      weaknesses: ['Algebra', 'Geometry'],
      curriculum: 'Checkpoint',
      subject: 'Mathematics',
      studentName: 'Charlotte',
    });

    expect(plan.lessons).toHaveLength(10);
    expect(plan.studentName).toBe('Charlotte');
    expect(plan.curriculum).toBe('Checkpoint');
    expect(plan.weaknesses).toEqual(['Algebra', 'Geometry']);
    expect(plan.lessons[0]?.addressesWeaknesses[0]).toBe('Algebra');
  });
});
