import { NextRequest, NextResponse } from 'next/server';
import {
  buildEssayReportPdfBytes,
  parseEssayAnalysisReport,
} from '@/lib/ai-analysis';

/**
 * POST /api/ai/essays/pdf — optional PDF export for an essay analysis report.
 *
 * Body: full EssayAnalysisReport JSON.
 */
export async function POST(req: NextRequest) {
  try {
    const body: unknown = await req.json();
    const report = parseEssayAnalysisReport(body);
    const pdfBytes = buildEssayReportPdfBytes(report);
    return new NextResponse(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="essay-analysis.pdf"',
      },
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to build essay PDF';
    return NextResponse.json({ error: message }, { status: 400 });
  }
}
