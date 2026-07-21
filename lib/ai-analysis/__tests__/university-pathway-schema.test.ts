/**
 * @jest-environment node
 */
import { parsePathwayRecommendation } from '../university-pathway-schema';
import { buildMockPathwayRecommendation } from '../university-pathway-prompts';

describe('university-pathway-schema', () => {
  it('test_parsePathwayRecommendation_validPayload_returnsRecommendation', () => {
    const recommendation = parsePathwayRecommendation({
      studentName: 'Charlotte',
      qualification: 'A-Level',
      grades: [{ subject: 'Mathematics', grade: 'A' }],
      summary: 'Strong STEM profile',
      universities: [
        {
          rank: 1,
          name: 'University of Auckland',
          region: 'New Zealand',
          admissionProbability: 80,
          rationale: 'Good fit',
        },
      ],
      majors: [
        {
          rank: 1,
          name: 'Computer Science',
          relatedSubjects: ['Mathematics'],
          admissionProbability: 75,
          rationale: 'Maths strength',
        },
      ],
      roadmapSteps: ['Confirm predicted grades'],
    });

    expect(recommendation.qualification).toBe('A-Level');
    expect(recommendation.universities).toHaveLength(1);
    expect(recommendation.majors[0]?.name).toBe('Computer Science');
  });

  it('test_parsePathwayRecommendation_emptyGrades_throws', () => {
    expect(() =>
      parsePathwayRecommendation({
        studentName: 'Charlotte',
        qualification: 'IGCSE',
        grades: [],
        summary: 'x',
        universities: [
          {
            rank: 1,
            name: 'U',
            region: 'UK',
            admissionProbability: 50,
            rationale: 'r',
          },
        ],
        majors: [
          {
            rank: 1,
            name: 'M',
            relatedSubjects: [],
            admissionProbability: 50,
            rationale: 'r',
          },
        ],
        roadmapSteps: [],
      }),
    ).toThrow();
  });

  it('test_buildMockPathwayRecommendation_ranksUniversitiesAndMajors', () => {
    const recommendation = buildMockPathwayRecommendation({
      grades: [
        { subject: 'Mathematics', grade: 'A' },
        { subject: 'Physics', grade: 'B' },
      ],
      qualification: 'IGCSE',
      studentName: 'Alex',
    });

    expect(recommendation.studentName).toBe('Alex');
    expect(recommendation.universities).toHaveLength(5);
    expect(recommendation.majors).toHaveLength(5);
    expect(recommendation.universities[0]?.rank).toBe(1);
  });
});
