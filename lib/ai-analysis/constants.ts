/** Maximum characters stored in extractedTextPreview. */
export const EXTRACTED_TEXT_PREVIEW_MAX_LENGTH = 500;

/** OpenAI model used for exam analysis when OPENAI_MODEL is unset. */
export const EXAM_ANALYSIS_MODEL = 'gpt-4o-mini';

export {
  CAMBRIDGE_PLAN_MAX_COMPLETION_TOKENS,
  DEFAULT_MAX_COMPLETION_TOKENS,
  DEFAULT_OPENAI_MODEL,
  PATHWAY_MAX_COMPLETION_TOKENS,
  PROMPT_INPUT_MAX_CHARS,
  resolveOpenAiModel,
  truncateForPrompt,
} from './model-config';

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
