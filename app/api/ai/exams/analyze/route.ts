import { NextRequest, NextResponse } from 'next/server';
import { analyzeExamFile } from '@/lib/ai-analysis';

/** POST /api/ai/exams/analyze — upload exam file and return structured AI report. */
export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get('file');

    if (!(file instanceof File)) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const report = await analyzeExamFile(file);
    return NextResponse.json(report);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to analyze exam';

    const status = message.includes('Unsupported file type') ||
      message.includes('File is empty') ||
      message.includes('No extractable text')
      ? 400
      : 500;

    return NextResponse.json({ error: message }, { status });
  }
}
