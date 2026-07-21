import type { EssayAnalysisReport } from './essay-schema';

function escapePdfText(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
}

/**
 * Build a minimal single-page PDF for an essay analysis report (optional AC).
 *
 * Uses a tiny hand-rolled PDF 1.4 writer — no extra npm dependency.
 *
 * @param report - Structured essay analysis report.
 * @returns PDF file bytes.
 */
export function buildEssayReportPdfBytes(report: EssayAnalysisReport): Uint8Array {
  const lines = [
    'Spinozah AI Education — Essay Analysis',
    `Student: ${report.studentName}`,
    `Title: ${report.title}`,
    `Grammar: ${report.grammarScore}/100`,
    `Vocabulary: ${report.vocabularyScore}/100`,
    `Structure: ${report.structureScore}/100`,
    `Summary: ${report.summary}`,
    'Rewrite suggestions (JSON):',
    JSON.stringify(report.suggestions),
  ];

  const contentLines = lines.flatMap((line, index) => {
    const y = 800 - index * 18;
    return [`BT /F1 11 Tf 40 ${y} Td (${escapePdfText(line.slice(0, 110))}) Tj ET`];
  });
  const stream = contentLines.join('\n');
  const streamLength = Buffer.byteLength(stream, 'utf8');

  const objects = [
    '1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj',
    '2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj',
    '3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj',
    `4 0 obj<< /Length ${streamLength} >>stream\n${stream}\nendstream endobj`,
    '5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj',
  ];

  let pdf = '%PDF-1.4\n';
  const offsets: number[] = [0];
  for (const object of objects) {
    offsets.push(Buffer.byteLength(pdf, 'utf8'));
    pdf += `${object}\n`;
  }
  const xrefStart = Buffer.byteLength(pdf, 'utf8');
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += '0000000000 65535 f \n';
  for (let i = 1; i < offsets.length; i += 1) {
    pdf += `${String(offsets[i]).padStart(10, '0')} 00000 n \n`;
  }
  pdf += `trailer<< /Size ${objects.length + 1} /Root 1 0 R >>\n`;
  pdf += `startxref\n${xrefStart}\n%%EOF`;

  return new TextEncoder().encode(pdf);
}
