import { NextRequest, NextResponse } from 'next/server';
import {
  buildPathwayReportPdfBytes,
  parsePathwayRecommendation,
} from '@/lib/ai-analysis';

/**
 * POST /api/ai/pathway/pdf — PDF export for a university pathway recommendation.
 *
 * Body: full PathwayRecommendation JSON.
 */
export async function POST(req: NextRequest) {
  try {
    const body: unknown = await req.json();
    const recommendation = parsePathwayRecommendation(body);
    const pdfBytes = buildPathwayReportPdfBytes(recommendation);
    return new NextResponse(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="university-pathway.pdf"',
      },
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to build pathway PDF';
    return NextResponse.json({ error: message }, { status: 400 });
  }
}
