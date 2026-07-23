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

  it('test_parsePathwayRecommendation_acceptsNceaAndIb', () => {
    for (const qualification of ['NCEA', 'IB'] as const) {
      const recommendation = parsePathwayRecommendation({
        studentName: 'Sam',
        qualification,
        grades: [{ subject: 'Mathematics', grade: qualification === 'IB' ? '6' : 'Excellence' }],
        summary: 'Profile ok',
        universities: [
          {
            rank: 1,
            name: 'University of Auckland',
            region: 'New Zealand',
            admissionProbability: 70,
            rationale: 'Fit',
          },
        ],
        majors: [
          {
            rank: 1,
            name: 'Computer Science',
            relatedSubjects: ['Mathematics'],
            admissionProbability: 68,
            rationale: 'Maths',
          },
        ],
        roadmapSteps: ['Confirm grades'],
      });
      expect(recommendation.qualification).toBe(qualification);
    }
  });

  it('test_buildMockPathwayRecommendation_nceaAndIb_preserveQualification', () => {
    const ncea = buildMockPathwayRecommendation({
      grades: [{ subject: 'Calculus', grade: 'Excellence' }],
      qualification: 'NCEA',
      studentName: 'Moana',
    });
    expect(ncea.qualification).toBe('NCEA');
    expect(ncea.universities[0]?.rationale).toContain('NCEA');

    const ib = buildMockPathwayRecommendation({
      grades: [{ subject: 'Mathematics HL', grade: '6' }],
      qualification: 'IB',
      studentName: 'Jordan',
    });
    expect(ib.qualification).toBe('IB');
    expect(ib.grades[0]?.grade).toBe('6');
  });
});
