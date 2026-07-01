import type { ExamAnalysisReport } from '@/lib/ai-analysis';

interface ExamReportViewProps {
  report: ExamAnalysisReport;
}

/** Renders a structured exam weakness report from the AI analysis API. */
export function ExamReportView({ report }: ExamReportViewProps) {
  return (
    <div className="mt-6 p-6 bg-slate-100 rounded-xl space-y-4">
      <h2 className="text-2xl font-bold">Structured Analysis Report</h2>

      <p>
        <strong>Student:</strong> {report.studentName}
      </p>
      <p>
        <strong>Subject:</strong> {report.subject}
      </p>
      <p>
        <strong>Total Score:</strong> {report.totalScore}
      </p>

      {report.strengths.length > 0 && (
        <div>
          <p className="font-semibold">Strengths</p>
          <ul className="list-disc pl-6 space-y-1">
            {report.strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {report.weakAreas.length > 0 && (
        <div>
          <p className="font-semibold">Weak Areas</p>
          <ul className="list-disc pl-6 space-y-1">
            {report.weakAreas.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {report.knowledgePoints.length > 0 && (
        <div>
          <p className="font-semibold">Knowledge Points</p>
          <ul className="list-disc pl-6 space-y-1">
            {report.knowledgePoints.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {report.questionBreakdown.length > 0 && (
        <div>
          <p className="font-semibold">Question Breakdown</p>
          <div className="bg-white p-4 rounded-lg border space-y-2">
            {report.questionBreakdown.map((question) => (
              <p key={question.questionNumber}>
                <strong>Q{question.questionNumber}</strong> — {question.topic}{' '}
                ({question.isCorrect ? 'Correct' : 'Incorrect'})
                {question.notes ? `: ${question.notes}` : ''}
              </p>
            ))}
          </div>
        </div>
      )}

      {report.recommendations.length > 0 && (
        <div>
          <p className="font-semibold">Recommended Teaching Focus</p>
          <ul className="list-disc pl-6 space-y-1">
            {report.recommendations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
