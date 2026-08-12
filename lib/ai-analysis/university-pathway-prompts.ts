import type {
  PathwayQualification,
  PathwayRecommendation,
  SubjectGrade,
} from './university-pathway-schema';

/** OpenAI model used for university pathway recommendations when OPENAI_MODEL is unset. */
export const UNIVERSITY_PATHWAY_MODEL = 'gpt-4o-mini';

/**
 * Slim system prompt: Zod validates the shape; cap list sizes for completion tokens.
 */
export const UNIVERSITY_PATHWAY_SYSTEM_PROMPT = `You are an expert university admissions counsellor for tutoring centers.
Given IGCSE, A-Level, NCEA, or IB grades, recommend ranked majors and universities.
Return ONLY valid JSON with: studentName, qualification (IGCSE|A-Level|NCEA|IB),
grades[{subject, grade}], summary, universities[{rank, name, region (UK|USA|Australia|New Zealand),
admissionProbability (0-100), rationale}], majors[{rank, name, relatedSubjects[],
admissionProbability, rationale}], roadmapSteps[] (max 5).
Return exactly 5 universities and 5 majors. Keep rationales to 1–2 short sentences.
Interpret grades for the qualification (letters/9–1, NCEA EMA, IB 1–7). Parent-friendly language.`;

export interface UniversityPathwayPromptInput {
  grades: SubjectGrade[];
  qualification: PathwayQualification;
  studentName?: string;
}

/**
 * Build the user prompt for pathway generation.
 *
 * @param input - Grades and qualification context.
 * @returns User message for the chat completion.
 */
export function buildUniversityPathwayUserPrompt(
  input: UniversityPathwayPromptInput,
): string {
  const nameHint = input.studentName?.trim()
    ? `Student name: "${input.studentName.trim()}".\n`
    : '';
  const gradeList = input.grades
    .map((item) => `- ${item.subject}: ${item.grade}`)
    .join('\n');

  return `${nameHint}Qualification: ${input.qualification}

Subject results:
${gradeList}

Recommend ranked universities and majors as JSON for parents.`;
}

/**
 * Deterministic mock recommendation when OPENAI_API_KEY is unset.
 *
 * @param input - Grades and qualification context.
 * @returns Validated-shaped pathway recommendation.
 */
export function buildMockPathwayRecommendation(
  input: UniversityPathwayPromptInput,
): PathwayRecommendation {
  const grades =
    input.grades.length > 0
      ? input.grades
      : [{ subject: 'Mathematics', grade: 'A' }];
  const studentName = input.studentName?.trim() || 'Unknown student';
  const subjects = grades.map((item) => item.subject);

  return {
    studentName,
    qualification: input.qualification,
    grades,
    summary:
      'Mock pathway (no OPENAI_API_KEY). Ranked universities and majors are illustrative for local development and parent preview.',
    universities: [
      {
        rank: 1,
        name: 'University of Auckland',
        region: 'New Zealand',
        admissionProbability: 78,
        rationale: `Strong match for ${subjects[0] ?? 'core'} results under ${input.qualification}.`,
      },
      {
        rank: 2,
        name: 'University of Melbourne',
        region: 'Australia',
        admissionProbability: 72,
        rationale: 'Competitive regional option with flexible entry pathways.',
      },
      {
        rank: 3,
        name: 'University of Manchester',
        region: 'UK',
        admissionProbability: 65,
        rationale: 'Solid UK target if predicted grades hold.',
      },
      {
        rank: 4,
        name: 'University of California, Davis',
        region: 'USA',
        admissionProbability: 58,
        rationale: 'US reach option; emphasise extracurriculars alongside grades.',
      },
      {
        rank: 5,
        name: 'University of Queensland',
        region: 'Australia',
        admissionProbability: 70,
        rationale: 'Balanced safety/target mix for the stated profile.',
      },
    ],
    majors: [
      {
        rank: 1,
        name: 'Computer Science',
        relatedSubjects: subjects.slice(0, 2),
        admissionProbability: 74,
        rationale: 'Aligns with quantitative strengths in the grade profile.',
      },
      {
        rank: 2,
        name: 'Engineering',
        relatedSubjects: subjects.filter((s) =>
          /math|physics|chem/i.test(s),
        ).length
          ? subjects.filter((s) => /math|physics|chem/i.test(s))
          : subjects.slice(0, 2),
        admissionProbability: 68,
        rationale: 'Builds on STEM subjects present in the results.',
      },
      {
        rank: 3,
        name: 'Business Analytics',
        relatedSubjects: subjects.slice(0, 2),
        admissionProbability: 71,
        rationale: 'Good fit when maths is strong and communication subjects exist.',
      },
      {
        rank: 4,
        name: 'Data Science',
        relatedSubjects: subjects.slice(0, 2),
        admissionProbability: 66,
        rationale: 'Growing field that rewards strong maths across curricula.',
      },
      {
        rank: 5,
        name: 'Economics',
        relatedSubjects: subjects.slice(0, 2),
        admissionProbability: 63,
        rationale: 'Balanced arts/STEM hybrid for versatile university applications.',
      },
    ],
    roadmapSteps: [
      'Confirm predicted grades with subject teachers.',
      'Shortlist 2–3 majors and matching universities by region.',
      'Draft personal statement / application essays early.',
      'Book admissions counselling follow-up before application deadlines.',
    ],
  };
}
