/**
 * @jest-environment node
 */
import {
  DEFAULT_OPENAI_MODEL,
  PROMPT_INPUT_MAX_CHARS,
  resolveOpenAiModel,
  truncateForPrompt,
} from '../model-config';
import { logAiUsage } from '../usage-logger';

describe('resolveOpenAiModel', () => {
  const originalModel = process.env.OPENAI_MODEL;

  afterEach(() => {
    if (originalModel === undefined) {
      delete process.env.OPENAI_MODEL;
    } else {
      process.env.OPENAI_MODEL = originalModel;
    }
  });

  it('test_resolveOpenAiModel_envUnset_returnsFeatureDefault', () => {
    delete process.env.OPENAI_MODEL;
    expect(resolveOpenAiModel('gpt-4o-mini')).toBe('gpt-4o-mini');
    expect(resolveOpenAiModel()).toBe(DEFAULT_OPENAI_MODEL);
  });

  it('test_resolveOpenAiModel_envSet_overridesDefault', () => {
    process.env.OPENAI_MODEL = 'gpt-4o';
    expect(resolveOpenAiModel('gpt-4o-mini')).toBe('gpt-4o');
  });

  it('test_resolveOpenAiModel_envBlank_usesDefault', () => {
    process.env.OPENAI_MODEL = '   ';
    expect(resolveOpenAiModel('gpt-4o-mini')).toBe('gpt-4o-mini');
  });
});

describe('truncateForPrompt', () => {
  it('test_truncateForPrompt_shortText_unchanged', () => {
    expect(truncateForPrompt('hello', 100)).toBe('hello');
  });

  it('test_truncateForPrompt_longText_addsOmissionMarker', () => {
    const long = 'a'.repeat(PROMPT_INPUT_MAX_CHARS + 500);
    const result = truncateForPrompt(long);
    expect(result.length).toBeLessThan(long.length);
    expect(result).toContain('truncated for prompt size');
    expect(result.startsWith('a'.repeat(PROMPT_INPUT_MAX_CHARS))).toBe(true);
  });
});

describe('logAiUsage', () => {
  it('test_logAiUsage_withUsage_returnsNormalizedPayload', () => {
    const infoSpy = jest.spyOn(console, 'info').mockImplementation(() => undefined);
    const started = Date.now() - 25;

    const payload = logAiUsage('exam', 'gpt-4o-mini', started, {
      prompt_tokens: 100,
      completion_tokens: 50,
      total_tokens: 150,
    });

    expect(payload.feature).toBe('exam');
    expect(payload.model).toBe('gpt-4o-mini');
    expect(payload.promptTokens).toBe(100);
    expect(payload.completionTokens).toBe(50);
    expect(payload.totalTokens).toBe(150);
    expect(payload.latencyMs).toBeGreaterThanOrEqual(0);
    expect(infoSpy).toHaveBeenCalledWith(
      '[ai-usage]',
      expect.stringContaining('"feature":"exam"'),
    );

    infoSpy.mockRestore();
  });

  it('test_logAiUsage_missingUsage_nullTokenFields', () => {
    const infoSpy = jest.spyOn(console, 'info').mockImplementation(() => undefined);
    const payload = logAiUsage('essay', 'gpt-4o-mini', Date.now());
    expect(payload.promptTokens).toBeNull();
    expect(payload.completionTokens).toBeNull();
    expect(payload.totalTokens).toBeNull();
    infoSpy.mockRestore();
  });
});
