'use client';

import { useState } from 'react';
import { UniversityPathwayView } from '@/components/university-pathway/UniversityPathwayView';
import { useUniversityPathway } from '@/hooks/useUniversityPathway';
import type { PathwayQualification, SubjectGrade } from '@/lib/ai-analysis';

const QUALIFICATION_OPTIONS: PathwayQualification[] = [
  'IGCSE',
  'A-Level',
  'NCEA',
  'IB',
];

const DEFAULT_GRADES_TEXT = `Mathematics: A
Physics: B
Chemistry: A
English: B`;

/**
 * Parse "Subject: Grade" lines (or comma-separated subject/grade pairs).
 *
 * @param text - Multiline grade input from the form.
 * @returns Parsed subject grades.
 */
function parseGradesText(text: string): SubjectGrade[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => {
      const colonIdx = line.indexOf(':');
      if (colonIdx === -1) {
        return null;
      }
      const subject = line.slice(0, colonIdx).trim();
      const grade = line.slice(colonIdx + 1).trim();
      if (!subject || !grade) {
        return null;
      }
      return { subject, grade };
    })
    .filter((item): item is SubjectGrade => item !== null);
}

/** University Pathway module: recommend majors/universities from exam results. */
export function UniversityPathwayPanel() {
  const [studentName, setStudentName] = useState('');
  const [qualification, setQualification] =
    useState<PathwayQualification>('A-Level');
  const [gradesText, setGradesText] = useState(DEFAULT_GRADES_TEXT);
  const { recommendation, isGenerating, error, generatePathway, reset } =
    useUniversityPathway();

  const grades = parseGradesText(gradesText);

  return (
    <div className="space-y-4 rounded-xl bg-white p-6 shadow">
      <p className="text-sm text-slate-600">
        Parent-facing pathway report: enter IGCSE, A-Level, NCEA, or IB results
        to get ranked majors and universities with admission chances.
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

      <label className="block text-sm font-medium text-slate-700">
        Qualification
        <select
          value={qualification}
          onChange={(event) => {
            setQualification(event.target.value as PathwayQualification);
            reset();
          }}
          className="mt-1 block w-full rounded-lg border p-2"
        >
          {QUALIFICATION_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label className="block text-sm font-medium text-slate-700">
        Results (one per line: Subject: Grade)
        <textarea
          value={gradesText}
          onChange={(event) => {
            setGradesText(event.target.value);
            reset();
          }}
          rows={6}
          className="mt-1 block w-full rounded-lg border p-2 font-mono text-sm"
          placeholder={'Mathematics: A\nPhysics: B'}
        />
      </label>

      <button
        type="button"
        disabled={grades.length === 0 || isGenerating}
        onClick={async () => {
          await generatePathway({
            grades,
            qualification,
            studentName: studentName.trim() || undefined,
          });
        }}
        className="w-full rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
      >
        {isGenerating ? 'Generating pathway…' : 'Generate university pathway'}
      </button>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {recommendation && (
        <UniversityPathwayView recommendation={recommendation} />
      )}
    </div>
  );
}
