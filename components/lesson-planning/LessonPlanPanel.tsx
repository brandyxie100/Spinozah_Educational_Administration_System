'use client';

import { useState } from 'react';
import { LessonPlanView } from '@/components/lesson-planning/LessonPlanView';
import { useCambridgePlan } from '@/hooks/useCambridgePlan';
import type { CambridgeCurriculum } from '@/lib/ai-analysis';

const CURRICULUM_OPTIONS: CambridgeCurriculum[] = [
  'Cambridge Primary',
  'Lower Secondary',
  'Checkpoint',
  'IGCSE',
  'AS Level',
  'A Level',
];

/** Lesson Planning module: generate a Cambridge plan from student weaknesses. */
export function LessonPlanPanel() {
  const [studentName, setStudentName] = useState('');
  const [curriculum, setCurriculum] = useState<CambridgeCurriculum>('IGCSE');
  const [subject, setSubject] = useState('Mathematics');
  const [weaknessesText, setWeaknessesText] = useState(
    'Fractions\nAlgebra\nGeometry',
  );
  const { plan, isGenerating, error, generatePlan, reset } = useCambridgePlan();

  const weaknesses = weaknessesText
    .split(/[\n,]+/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0);

  return (
    <div className="space-y-4 rounded-xl bg-white p-6 shadow">
      <p className="text-sm text-slate-600">
        Cambridge-aware planner: map student weaknesses into a structured 10-lesson
        teaching plan with objectives, activities, and homework.
      </p>

      <label className="block text-sm font-medium text-slate-700">
        Student name (optional)
        <input
          type="text"
          value={studentName}
          onChange={(event) => setStudentName(event.target.value)}
          className="mt-1 block w-full rounded-lg border p-2"
          placeholder="e.g. Charlotte"
        />
      </label>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block text-sm font-medium text-slate-700">
          Curriculum
          <select
            value={curriculum}
            onChange={(event) => {
              setCurriculum(event.target.value as CambridgeCurriculum);
              reset();
            }}
            className="mt-1 block w-full rounded-lg border p-2"
          >
            {CURRICULUM_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm font-medium text-slate-700">
          Subject
          <input
            type="text"
            value={subject}
            onChange={(event) => setSubject(event.target.value)}
            className="mt-1 block w-full rounded-lg border p-2"
            placeholder="e.g. Mathematics"
          />
        </label>
      </div>

      <label className="block text-sm font-medium text-slate-700">
        Student weaknesses (one per line or comma-separated)
        <textarea
          value={weaknessesText}
          onChange={(event) => {
            setWeaknessesText(event.target.value);
            reset();
          }}
          rows={5}
          className="mt-1 block w-full rounded-lg border p-2 font-mono text-sm"
          placeholder={'Fractions\nAlgebra\nProbability'}
        />
      </label>

      <button
        type="button"
        disabled={weaknesses.length === 0 || !subject.trim() || isGenerating}
        onClick={async () => {
          await generatePlan({
            weaknesses,
            curriculum,
            subject: subject.trim(),
            studentName: studentName.trim() || undefined,
          });
        }}
        className="w-full rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
      >
        {isGenerating ? 'Generating plan…' : 'Generate Cambridge teaching plan'}
      </button>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {plan && <LessonPlanView plan={plan} />}
    </div>
  );
}
