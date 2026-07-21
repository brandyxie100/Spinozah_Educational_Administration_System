import { NextRequest, NextResponse } from 'next/server';
import { analyzeEssayFile, analyzeEssayText } from '@/lib/ai-analysis';

/**
 * POST /api/ai/essays/analyze
 *
 * Accepts either:
 * - multipart `file` (PDF/image essay upload), or
 * - multipart/json field `text` (pasted essay body)
 * Optional: `studentName`
 */
export async function POST(req: NextRequest) {
  try {
    const contentType = req.headers.get('content-type') ?? '';

    if (contentType.includes('application/json')) {
      const body = (await req.json()) as {
        text?: unknown;
        studentName?: unknown;
      };
      if (typeof body.text !== 'string' || !body.text.trim()) {
        return NextResponse.json({ error: 'No essay text provided' }, { status: 400 });
      }
      const studentName =
        typeof body.studentName === 'string' ? body.studentName : undefined;
      const report = await analyzeEssayText(body.text, { studentName });
      return NextResponse.json(report);
    }

    const formData = await req.formData();
    const file = formData.get('file');
    const textField = formData.get('text');
    const studentNameField = formData.get('studentName');
    const studentName =
      typeof studentNameField === 'string' ? studentNameField : undefined;

    if (file instanceof File) {
      const report = await analyzeEssayFile(file);
      return NextResponse.json(report);
    }

    if (typeof textField === 'string' && textField.trim()) {
      const report = await analyzeEssayText(textField, { studentName });
      return NextResponse.json(report);
    }

    return NextResponse.json(
      { error: 'Provide an essay file upload or text field' },
      { status: 400 },
    );
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to analyze essay';

    const status =
      message.includes('Unsupported file type') ||
      message.includes('File is empty') ||
      message.includes('No essay text') ||
      message.includes('No extractable text')
        ? 400
        : 500;

    return NextResponse.json({ error: message }, { status });
  }
}
