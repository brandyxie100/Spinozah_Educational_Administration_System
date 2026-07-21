import type { CambridgeTeachingPlan } from '@/lib/ai-analysis';

interface LessonPlanViewProps {
  plan: CambridgeTeachingPlan;
}

/** Renders a structured Cambridge teaching plan from weaknesses. */
export function LessonPlanView({ plan }: LessonPlanViewProps) {
  return (
    <div className="mt-6 space-y-4 rounded-xl bg-slate-100 p-6">
      <h2 className="text-2xl font-bold">Cambridge Teaching Plan</h2>

      <p>
        <strong>Student:</strong> {plan.studentName}
      </p>
      <p>
        <strong>Curriculum:</strong> {plan.curriculum}
      </p>
      <p>
        <strong>Subject:</strong> {plan.subject}
      </p>
      <p>
        <strong>Summary:</strong> {plan.summary}
      </p>

      <div>
        <p className="font-semibold">Weaknesses addressed</p>
        <ul className="list-disc space-y-1 pl-6">
          {plan.weaknesses.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      {plan.focusTopics.length > 0 && (
        <div>
          <p className="font-semibold">Focus topics</p>
          <ul className="list-disc space-y-1 pl-6">
            {plan.focusTopics.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="space-y-4">
        <p className="font-semibold">Lessons ({plan.lessons.length})</p>
        {plan.lessons.map((lesson) => (
          <article
            key={lesson.lessonNumber}
            className="rounded-lg border bg-white p-4"
          >
            <h3 className="text-lg font-bold">
              {lesson.lessonNumber}. {lesson.title}
            </h3>
            <div className="mt-2 grid gap-3 sm:grid-cols-2">
              <div>
                <p className="text-sm font-medium text-slate-500">Objectives</p>
                <ul className="list-disc pl-5 text-sm">
                  {lesson.objectives.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">Activities</p>
                <ul className="list-disc pl-5 text-sm">
                  {lesson.activities.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
            <p className="mt-2 text-sm">
              <strong>Homework:</strong> {lesson.homework}
            </p>
            {lesson.addressesWeaknesses.length > 0 && (
              <p className="mt-1 text-sm text-slate-600">
                Targets: {lesson.addressesWeaknesses.join(', ')}
              </p>
            )}
          </article>
        ))}
      </div>

      <details className="rounded-lg border bg-white p-4">
        <summary className="cursor-pointer font-semibold">Plan JSON</summary>
        <pre className="mt-2 overflow-auto text-xs text-slate-700">
          {JSON.stringify(plan, null, 2)}
        </pre>
      </details>
    </div>
  );
}
