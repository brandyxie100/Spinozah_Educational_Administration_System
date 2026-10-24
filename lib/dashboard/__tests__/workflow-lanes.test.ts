/**
 * @jest-environment node
 */
import { WORKFLOW_LANES } from '../workflow-lanes';

describe('WORKFLOW_LANES', () => {
  it('test_workflowLanes_coversFifteenModules_uniqueTitles', () => {
    const titles = WORKFLOW_LANES.flatMap((lane) =>
      lane.modules.map((m) => m.title),
    );
    expect(titles).toHaveLength(15);
    expect(new Set(titles).size).toBe(15);
  });

  it('test_workflowLanes_includesKnownModules', () => {
    const titles = new Set(
      WORKFLOW_LANES.flatMap((lane) => lane.modules.map((m) => m.title)),
    );
    expect(titles.has('Admin Dashboard')).toBe(true);
    expect(titles.has('University Pathway')).toBe(true);
    expect(titles.has('Teacher Management')).toBe(true);
  });
});
