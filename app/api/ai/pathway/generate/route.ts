import { NextRequest, NextResponse } from 'next/server';
import {
  generateUniversityPathway,
  pathwayQualificationSchema,
  subjectGradeSchema,
} from '@/lib/ai-analysis';

/**
 * POST /api/ai/pathway/generate
 *
 * Body JSON: { grades: [{subject, grade}], qualification?, studentName? }
 * Returns ranked universities and majors for parents.
 */
export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as {
      grades?: unknown;
      qualification?: unknown;
      studentName?: unknown;
    };

    if (!Array.isArray(body.grades)) {
      return NextResponse.json(
        { error: 'grades must be a non-empty array of { subject, grade }' },
        { status: 400 },
      );
    }

    const grades = body.grades
      .map((item) => subjectGradeSchema.safeParse(item))
      .filter((result) => result.success)
      .map((result) => result.data);

    if (grades.length === 0) {
      return NextResponse.json(
        { error: 'At least one subject grade is required' },
        { status: 400 },
      );
    }

    let qualification:
      | ReturnType<typeof pathwayQualificationSchema.parse>
      | undefined;
    if (body.qualification !== undefined && body.qualification !== null) {
      const parsed = pathwayQualificationSchema.safeParse(body.qualification);
      if (!parsed.success) {
        return NextResponse.json(
          { error: 'qualification must be IGCSE, A-Level, NCEA, or IB' },
          { status: 400 },
        );
      }
      qualification = parsed.data;
    }

    const studentName =
      typeof body.studentName === 'string' ? body.studentName : undefined;

    const recommendation = await generateUniversityPathway(grades, {
      qualification,
      studentName,
    });

    return NextResponse.json(recommendation);
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : 'Failed to generate university pathway';

    const status =
      message.includes('grade') || message.includes('OPENAI_API_KEY')
        ? 400
        : 500;

    return NextResponse.json({ error: message }, { status });
  }
}
