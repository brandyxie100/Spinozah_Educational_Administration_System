/**
 * @jest-environment node
 */
import { PROMPT_INPUT_MAX_CHARS } from '../model-config';
import { buildExamAnalysisUserPrompt } from '../prompts';
import { buildEssayAnalysisUserPrompt } from '../essay-prompts';

describe('prompt input truncation', () => {
  it('test_buildExamAnalysisUserPrompt_longText_truncates', () => {
    const long = 'q'.repeat(PROMPT_INPUT_MAX_CHARS + 100);
    const prompt = buildExamAnalysisUserPrompt(long, 'Ada');
    expect(prompt).toContain('Ada');
    expect(prompt).toContain('truncated for prompt size');
    expect(prompt.length).toBeLessThan(long.length + 200);
  });

  it('test_buildEssayAnalysisUserPrompt_longText_truncates', () => {
    const long = 'e'.repeat(PROMPT_INPUT_MAX_CHARS + 100);
    const prompt = buildEssayAnalysisUserPrompt(long);
    expect(prompt).toContain('truncated for prompt size');
  });
});
