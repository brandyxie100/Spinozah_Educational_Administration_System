import { NextRequest, NextResponse } from 'next/server';
import {
  cambridgeCurriculumSchema,
  generateCambridgeTeachingPlan,
} from '@/lib/ai-analysis';

/**
 * POST /api/ai/plans/generate
 *
 * Body JSON: { weaknesses: string[], curriculum?, subject?, studentName? }
 * Returns a structured Cambridge teaching plan.
 */
export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as {
      weaknesses?: unknown;
      curriculum?: unknown;
      subject?: unknown;
      studentName?: unknown;
    };

    if (!Array.isArray(body.weaknesses)) {
      return NextResponse.json(
        { error: 'weaknesses must be a non-empty string array' },
        { status: 400 },
      );
    }

    const weaknesses = body.weaknesses.filter(
      (item): item is string => typeof item === 'string',
    );

    if (weaknesses.length === 0) {
      return NextResponse.json(
        { error: 'At least one student weakness is required' },
        { status: 400 },
      );
    }

    let curriculum: ReturnType<typeof cambridgeCurriculumSchema.parse> | undefined;
    if (body.curriculum !== undefined && body.curriculum !== null) {
      const parsed = cambridgeCurriculumSchema.safeParse(body.curriculum);
      if (!parsed.success) {
        return NextResponse.json(
          { error: 'Invalid Cambridge curriculum level' },
          { status: 400 },
        );
      }
      curriculum = parsed.data;
    }

    const subject = typeof body.subject === 'string' ? body.subject : undefined;
    const studentName =
      typeof body.studentName === 'string' ? body.studentName : undefined;

    const plan = await generateCambridgeTeachingPlan(weaknesses, {
      curriculum,
      subject,
      studentName,
    });

    return NextResponse.json(plan);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to generate Cambridge plan';

    const status =
      message.includes('weakness') || message.includes('OPENAI_API_KEY')
        ? 400
        : 500;

    return NextResponse.json({ error: message }, { status });
  }
}
