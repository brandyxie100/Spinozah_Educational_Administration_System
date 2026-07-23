import type { PathwayRecommendation } from './university-pathway-schema';

function escapePdfText(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
}

/**
 * Build a minimal single-page PDF for a university pathway recommendation.
 *
 * Uses a tiny hand-rolled PDF 1.4 writer — same approach as essay PDF (no extra dep).
 *
 * @param recommendation - Structured pathway recommendation.
 * @returns PDF file bytes.
 */
export function buildPathwayReportPdfBytes(
  recommendation: PathwayRecommendation,
): Uint8Array {
  const topMajors = recommendation.majors
    .slice(0, 3)
    .map((major) => `#${major.rank} ${major.name} (${major.admissionProbability}%)`)
    .join('; ');
  const topUnis = recommendation.universities
    .slice(0, 3)
    .map(
      (uni) =>
        `#${uni.rank} ${uni.name} [${uni.region}] (${uni.admissionProbability}%)`,
    )
    .join('; ');
  const grades = recommendation.grades
    .slice(0, 6)
    .map((item) => `${item.subject}: ${item.grade}`)
    .join('; ');

  const lines = [
    'Spinozah AI Education — University Pathway',
    `Student: ${recommendation.studentName}`,
    `Qualification: ${recommendation.qualification}`,
    `Grades: ${grades}`,
    `Summary: ${recommendation.summary}`,
    `Top majors: ${topMajors}`,
    `Top universities: ${topUnis}`,
    `Next steps: ${recommendation.roadmapSteps.slice(0, 3).join(' | ')}`,
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
