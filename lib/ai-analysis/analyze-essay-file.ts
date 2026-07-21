import { extractTextFromExamFile, inferStudentNameFromFilename } from './analyze-exam-file';
import { analyzeEssayText } from './essay-analyzer';
import type { EssayAnalysisReport } from './essay-schema';

/**
 * End-to-end essay analysis from an uploaded file (PDF/image).
 *
 * @param file - Uploaded essay file from FormData.
 * @returns Structured scores and rewrite suggestions.
 */
export async function analyzeEssayFile(file: File): Promise<EssayAnalysisReport> {
  if (file.size === 0) {
    throw new Error('File is empty');
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);
  const extractedText = await extractTextFromExamFile(buffer, file.type);
  const studentName = inferStudentNameFromFilename(file.name);

  return analyzeEssayText(extractedText, { studentName });
}
