/**
 * @jest-environment node
 */
import type OpenAI from 'openai';
import { analyzeEssayText } from '../essay-analyzer';
import { buildEssayReportPdfBytes } from '../essay-pdf';
import { buildMockEssayAnalysisReport } from '../essay-prompts';
import { parseEssayAnalysisReport } from '../essay-schema';

const validOpenAiPayload = {
  studentName: 'Charlotte',
  title: 'My Summer Holiday',
  grammarScore: 80,
  vocabularyScore: 75,
  structureScore: 78,
  cohesionNotes: ['Clear paragraph order'],
  suggestions: {
    grammarImprovements: ['Watch article usage'],
    advancedVocabulary: ['Use "memorable" instead of "nice"'],
    sentenceRewrites: [
      {
        original: 'It was nice.',
        rewrite: 'It was a memorable experience.',
      },
    ],
  },
  summary: 'Solid draft with room for richer vocabulary.',
};

function createMockOpenAI(content: string): OpenAI {
  return {
    chat: {
      completions: {
        create: jest.fn().mockResolvedValue({
          choices: [{ message: { content } }],
        }),
      },
    },
  } as unknown as OpenAI;
}

describe('analyzeEssayText', () => {
  it('returns parsed scores and rewrite suggestions from OpenAI JSON', async () => {
    const client = createMockOpenAI(JSON.stringify(validOpenAiPayload));
    const report = await analyzeEssayText('It was nice. We went to the beach.', {
      openai: client,
      studentName: 'Charlotte',
    });
    expect(report.grammarScore).toBe(80);
    expect(report.suggestions.sentenceRewrites[0]?.rewrite).toContain('memorable');
    expect(report.extractedTextPreview).toContain('beach');
  });

  it('returns mock report when API key is missing', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;
    const report = await analyzeEssayText('Hello world essay about friendship.');
    expect(report.grammarScore).toBeGreaterThan(0);
    expect(report.suggestions.grammarImprovements.length).toBeGreaterThan(0);
    process.env.OPENAI_API_KEY = originalKey;
  });

  it('throws on empty essay text', async () => {
    await expect(analyzeEssayText('   ')).rejects.toThrow('No essay text provided');
  });
});

describe('essay PDF helper', () => {
  it('builds non-empty PDF bytes from a report', () => {
    const report = parseEssayAnalysisReport(
      buildMockEssayAnalysisReport('A short essay about schools.'),
    );
    const pdf = buildEssayReportPdfBytes(report);
    expect(pdf.byteLength).toBeGreaterThan(100);
    expect(Buffer.from(pdf).subarray(0, 4).toString()).toBe('%PDF');
  });
});
