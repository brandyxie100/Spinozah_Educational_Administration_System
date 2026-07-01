import { NextRequest, NextResponse } from 'next/server';
import { extractTextFromExamFile } from '@/lib/ai-analysis';

/**
 * Legacy PDF text extraction endpoint.
 * Prefer POST /api/ai/exams/analyze for full structured analysis.
 */
export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get('file');

    if (!(file instanceof File)) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const text = await extractTextFromExamFile(buffer, file.type);

    return NextResponse.json({ text });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : 'Failed to parse uploaded file';

    return NextResponse.json({ error: message }, { status: 500 });
  }
}
