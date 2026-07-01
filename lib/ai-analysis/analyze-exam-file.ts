import { analyzeExamText } from './analyzer';
import {
  SUPPORTED_IMAGE_MIME_TYPES,
  SUPPORTED_MIME_TYPES,
} from './constants';
import { extractTextFromImage } from './extract-image';
import { extractTextFromPdf } from './extract-pdf';
import type { ExamAnalysisReport } from './schema';

/**
 * Derive a student name hint from an uploaded filename.
 *
 * @param filename - Original file name from the upload.
 * @returns First token before space or extension, or empty string.
 */
export function inferStudentNameFromFilename(filename: string): string {
  const baseName = filename.split('.')[0] ?? '';
  const firstToken = baseName.split(' ')[0] ?? '';
  return firstToken.trim();
}

/**
 * Extract plain text from an uploaded exam file by MIME type.
 *
 * @param buffer - File bytes.
 * @param mimeType - Browser-reported MIME type.
 * @returns Extracted document text.
 */
export async function extractTextFromExamFile(
  buffer: Buffer,
  mimeType: string,
): Promise<string> {
  if (mimeType === SUPPORTED_MIME_TYPES.PDF) {
    return extractTextFromPdf(buffer);
  }

  if (SUPPORTED_IMAGE_MIME_TYPES.includes(mimeType)) {
    return extractTextFromImage(buffer);
  }

  throw new Error(
    `Unsupported file type: ${mimeType}. Upload PDF, JPEG, PNG, or WebP.`,
  );
}

/**
 * End-to-end exam analysis: extract text then call OpenAI.
 *
 * @param file - Uploaded exam file from FormData.
 * @returns Structured weakness report.
 */
export async function analyzeExamFile(file: File): Promise<ExamAnalysisReport> {
  if (file.size === 0) {
    throw new Error('File is empty');
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);
  const extractedText = await extractTextFromExamFile(buffer, file.type);
  const studentName = inferStudentNameFromFilename(file.name);

  return analyzeExamText(extractedText, { studentName });
}
