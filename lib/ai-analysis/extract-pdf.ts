import { PDFParse } from 'pdf-parse';

/**
 * Extract plain text from a PDF buffer using pdf-parse v2.
 *
 * @param buffer - Raw PDF bytes.
 * @returns Trimmed document text.
 */
export async function extractTextFromPdf(buffer: Buffer): Promise<string> {
  const parser = new PDFParse({ data: buffer });

  try {
    const result = await parser.getText();
    return result.text.trim();
  } finally {
    await parser.destroy();
  }
}
