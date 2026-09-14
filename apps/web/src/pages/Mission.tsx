import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

type Criterion = {
  id: string
  name: string
  passed: boolean
  evidence: string
}

type Evaluation = {
  score: number
  passed: boolean
  criteria: Criterion[]
  strengths: string[]
  weaknesses: string[]
  feedback: string
  next_action: string
}

type ApiResponse = {
  status: string
  mission_id: string
  result: Evaluation
}

export default function Mission() {
  const { missionId } = useParams()

  const [attempt, setAttempt] = useState('')
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const trimmedAttempt = attempt.trim()

    if (!trimmedAttempt || isSubmitting) {
      return
    }

    setIsSubmitting(true)
    setError('')
    setEvaluation(null)

    try {
      const response = await fetch(
        `http://localhost:8080/api/missions/${missionId ?? '1'}/attempt`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            learner_id: 'demo-learner',
            skill: 'python',
            level: 'beginner',
            mission: 'Build an authenticated API',
            attempt: trimmedAttempt,
            attempt_type: 'text',
          }),
        },
      )

      const data = await response.json()

      if (!response.ok) {
        const message =
          typeof data.detail === 'string'
            ? data.detail
            : data.detail?.message ||
              'The learning evaluation failed.'

        throw new Error(message)
      }

      const result = data as ApiResponse

      setEvaluation(result.result)
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : 'Something went wrong while submitting your attempt.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="mission-page">
      <nav className="mission-nav">
        <Link to="/dashboard">← Back to dashboard</Link>

        <span>Mission {missionId}</span>
      </nav>

      <section className="mission-header">
        <span className="eyebrow">PRACTICAL MISSION</span>

        <h1>Build an authenticated API</h1>

        <p>
          Complete this practical challenge to continue your mastery journey.
          Your work will become the basis for the next evaluation and challenge.
        </p>
      </section>

      <section className="mission-content">
        <article className="mission-card">
          <div className="card-header">
            <div>
              <span className="eyebrow">YOUR CHALLENGE</span>

              <h2>Build a protected REST API</h2>
            </div>

            <span className="status">ACTIVE</span>
          </div>

          <p>
            Build a REST API with Python that allows authenticated users to
            create, read, update, and delete learning resources.
          </p>

          <h3>Requirements</h3>

          <ul>
            <li>Create a REST API using Python.</li>
            <li>Implement authentication for protected endpoints.</li>
            <li>
              Allow authenticated users to manage learning resources.
            </li>
            <li>Return appropriate HTTP status codes.</li>
            <li>
              Document how another developer can run and test your API.
            </li>
          </ul>

          <h3>What you need to prove</h3>

          <p>
            Don't just explain how you would build it. Show what you actually
            built and how it works.
          </p>
        </article>

        <form
          className="submission-card"
          onSubmit={handleSubmit}
        >
          <div>
            <span className="eyebrow">YOUR ATTEMPT</span>

            <h2>Show what you built</h2>

            <p>
              Describe your implementation, provide the relevant repository
              or API details, and explain how authentication works.
            </p>
          </div>

          <label htmlFor="attempt">
            Your submission
          </label>

          <textarea
            id="attempt"
            name="attempt"
            value={attempt}
            onChange={(event) => {
              setAttempt(event.target.value)
              setEvaluation(null)
              setError('')
            }}
            placeholder="Describe what you built, how you implemented authentication, and how someone can test your API..."
            rows={12}
            required
          />

          <div className="submission-footer">
            <span>{attempt.length} characters</span>

            <button
              type="submit"
              disabled={!attempt.trim() || isSubmitting}
            >
              {isSubmitting
                ? 'Evaluating...'
                : 'Submit attempt →'}
            </button>
          </div>

          {error && (
            <div
              className="submission-error"
              role="alert"
            >
              <strong>Evaluation failed</strong>

              <p>{error}</p>
            </div>
          )}

          {evaluation && (
            <section
              className="evaluation-result"
              aria-live="polite"
            >
              <div className="evaluation-header">
                <div>
                  <span className="eyebrow">
                    EVALUATION COMPLETE
                  </span>

                  <h2>
                    {evaluation.passed
                      ? 'Mission passed'
                      : 'Keep building'}
                  </h2>
                </div>

                <div className="evaluation-score">
                  <strong>{evaluation.score}</strong>

                  <span>/100</span>
                </div>
              </div>

              <div className="criteria-list">
                <h3>What you proved</h3>

                {evaluation.criteria.map((criterion) => (
                  <article
                    className="criterion"
                    key={criterion.id}
                  >
                    <div className="criterion-header">
                      <strong>{criterion.name}</strong>

                      <span
                        className={
                          criterion.passed
                            ? 'criterion-passed'
                            : 'criterion-failed'
                        }
                      >
                        {criterion.passed
                          ? 'PASSED'
                          : 'NOT PROVEN'}
                      </span>
                    </div>

                    <p>{criterion.evidence}</p>
                  </article>
                ))}
              </div>

              {evaluation.strengths.length > 0 && (
                <div className="evaluation-section">
                  <h3>Strengths</h3>

                  <ul>
                    {evaluation.strengths.map(
                      (strength, index) => (
                        <li key={index}>
                          {strength}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}

              {evaluation.weaknesses.length > 0 && (
                <div className="evaluation-section">
                  <h3>Areas to improve</h3>

                  <ul>
                    {evaluation.weaknesses.map(
                      (weakness, index) => (
                        <li key={index}>
                          {weakness}
                        </li>
                      ),
                    )}
                  </ul>
                </div>
              )}

              <div className="evaluation-section">
                <h3>Feedback</h3>

                <p>{evaluation.feedback}</p>
              </div>

              <div className="next-action">
                <span className="eyebrow">
                  NEXT ACTION
                </span>

                <h3>{evaluation.next_action}</h3>
              </div>
            </section>
          )}
        </form>
      </section>
    </main>
  )
}