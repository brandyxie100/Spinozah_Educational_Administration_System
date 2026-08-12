/**
 * @jest-environment node
 */
import { resolveDeepAgentModel, runExamToPlanWithDeepAgent } from '../deep-agents/exam-to-plan-orchestrator';

describe('resolveDeepAgentModel', () => {
  const originalModel = process.env.OPENAI_MODEL;

  afterEach(() => {
    if (originalModel === undefined) {
      delete process.env.OPENAI_MODEL;
    } else {
      process.env.OPENAI_MODEL = originalModel;
    }
  });

  it('test_resolveDeepAgentModel_plainId_prefixesOpenai', () => {
    delete process.env.OPENAI_MODEL;
    expect(resolveDeepAgentModel('gpt-4o-mini')).toBe('openai:gpt-4o-mini');
  });

  it('test_resolveDeepAgentModel_alreadyPrefixed_unchanged', () => {
    process.env.OPENAI_MODEL = 'openai:gpt-4o';
    expect(resolveDeepAgentModel()).toBe('openai:gpt-4o');
  });
});

describe('runExamToPlanWithDeepAgent', () => {
  it('test_runExamToPlanWithDeepAgent_emptyText_throws', async () => {
    await expect(
      runExamToPlanWithDeepAgent({ examText: '   ' }),
    ).rejects.toThrow('Exam text is required');
  });

  it('test_runExamToPlanWithDeepAgent_noApiKey_returnsMockPlan', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;
    const infoSpy = jest.spyOn(console, 'info').mockImplementation(() => undefined);

    const result = await runExamToPlanWithDeepAgent({
      examText: 'Sample exam Q1 wrong fraction.',
      studentName: 'Ada',
      curriculum: 'IGCSE',
      subject: 'Mathematics',
    });

    expect(result.plan.studentName).toBe('Ada');
    expect(result.plan.lessons).toHaveLength(10);
    expect(result.model).toContain('openai:');
    expect(infoSpy).toHaveBeenCalledWith(
      '[ai-usage]',
      expect.stringContaining('deep_agent_exam_to_plan'),
    );

    infoSpy.mockRestore();
    process.env.OPENAI_API_KEY = originalKey;
  });

  it('test_runExamToPlanWithDeepAgent_noApiKeyStrict_throws', async () => {
    const originalKey = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;

    await expect(
      runExamToPlanWithDeepAgent(
        { examText: 'Sample exam' },
        { allowMockWithoutApiKey: false },
      ),
    ).rejects.toThrow('OPENAI_API_KEY');

    process.env.OPENAI_API_KEY = originalKey;
  });
});
