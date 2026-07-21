import type { PathwayRecommendation } from '@/lib/ai-analysis';

interface UniversityPathwayViewProps {
  recommendation: PathwayRecommendation;
}

/** Parent-facing view of ranked universities and majors. */
export function UniversityPathwayView({
  recommendation,
}: UniversityPathwayViewProps) {
  return (
    <div className="mt-6 space-y-4 rounded-xl bg-slate-100 p-6">
      <h2 className="text-2xl font-bold">University Pathway Report</h2>

      <p>
        <strong>Student:</strong> {recommendation.studentName}
      </p>
      <p>
        <strong>Qualification:</strong> {recommendation.qualification}
      </p>
      <p>
        <strong>Summary:</strong> {recommendation.summary}
      </p>

      <div>
        <p className="font-semibold">Results used</p>
        <ul className="list-disc space-y-1 pl-6">
          {recommendation.grades.map((item) => (
            <li key={`${item.subject}-${item.grade}`}>
              {item.subject}: {item.grade}
            </li>
          ))}
        </ul>
      </div>

      <div>
        <p className="font-semibold">Recommended majors</p>
        <div className="mt-2 space-y-3">
          {recommendation.majors.map((major) => (
            <article key={major.rank} className="rounded-lg border bg-white p-4">
              <h3 className="font-bold">
                #{major.rank} {major.name}
              </h3>
              <p className="text-sm text-slate-600">
                Admission chance: {major.admissionProbability}%
              </p>
              <p className="mt-1 text-sm">{major.rationale}</p>
              {major.relatedSubjects.length > 0 && (
                <p className="mt-1 text-sm text-slate-500">
                  Related: {major.relatedSubjects.join(', ')}
                </p>
              )}
            </article>
          ))}
        </div>
      </div>

      <div>
        <p className="font-semibold">Recommended universities</p>
        <div className="mt-2 space-y-3">
          {recommendation.universities.map((uni) => (
            <article key={uni.rank} className="rounded-lg border bg-white p-4">
              <h3 className="font-bold">
                #{uni.rank} {uni.name}
              </h3>
              <p className="text-sm text-slate-600">
                {uni.region} · Admission chance: {uni.admissionProbability}%
              </p>
              <p className="mt-1 text-sm">{uni.rationale}</p>
            </article>
          ))}
        </div>
      </div>

      {recommendation.roadmapSteps.length > 0 && (
        <div>
          <p className="font-semibold">Next steps</p>
          <ol className="list-decimal space-y-1 pl-6">
            {recommendation.roadmapSteps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      <details className="rounded-lg border bg-white p-4">
        <summary className="cursor-pointer font-semibold">Pathway JSON</summary>
        <pre className="mt-2 overflow-auto text-xs text-slate-700">
          {JSON.stringify(recommendation, null, 2)}
        </pre>
      </details>
    </div>
  );
}
