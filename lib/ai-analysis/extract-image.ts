import Tesseract from 'tesseract.js';

/** Default OCR language for exam images. */
const OCR_LANGUAGE = 'eng';

/**
 * Extract plain text from an image buffer using Tesseract OCR.
 *
 * @param buffer - Raw image bytes (JPEG, PNG, or WebP).
 * @returns Trimmed OCR text.
 */
export async function extractTextFromImage(buffer: Buffer): Promise<string> {
  const { data } = await Tesseract.recognize(buffer, OCR_LANGUAGE);
  return data.text.trim();
}
