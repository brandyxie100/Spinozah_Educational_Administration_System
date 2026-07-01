/** Maximum characters stored in extractedTextPreview. */
export const EXTRACTED_TEXT_PREVIEW_MAX_LENGTH = 500;

/** OpenAI model used for exam analysis. */
export const EXAM_ANALYSIS_MODEL = 'gpt-4o-mini';

export const SUPPORTED_MIME_TYPES = {
  PDF: 'application/pdf',
  JPEG: 'image/jpeg',
  PNG: 'image/png',
  WEBP: 'image/webp',
} as const;

export const SUPPORTED_IMAGE_MIME_TYPES: readonly string[] = [
  SUPPORTED_MIME_TYPES.JPEG,
  SUPPORTED_MIME_TYPES.PNG,
  SUPPORTED_MIME_TYPES.WEBP,
];
