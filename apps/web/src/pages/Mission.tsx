import { useEffect, useState } from 'react'
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
}

type MissionDetails = {
  id: string
  title: string
  description: string
  skills?: string[]
}

type MissionResponse = MissionDetails & {
  mission: string
  skill: string
}

type TargetedExercise = {
  status: string
  skill: string
  exercise: {
    title: string
    objective: string
    instructions: string[]
    success_signal: string
    targeted_skills: string[]
    targeted_criteria: string[]
  }
  next_action: string
}

type NextMission = {
  id: string
  skill: string
  title: string
  description: string
  skills: string[]
}

type AdaptedMission = {
  status: string
  learner_id: string
  skill: string
  score: number
  passed: boolean
  strengths: string[]
  weaknesses: string[]
  targeted_exercise?: TargetedExercise
  next_action: string
  next_mission?: NextMission | null
  message?: string
}

type LearningState = {
  learner_id: string
  skill: string
  level: string
  goal: Record<string, unknown> | null
  mission: MissionResponse | null
  latest_attempt: unknown
  attempt_text: string | null
  attempt_type: string
  evaluation: Evaluation | null
  weaknesses: string[] | null
  targeted_exercise: TargetedExercise | null
  adapted_mission: AdaptedMission | null
  next_action: string
}

type StartLearningResponse = {
  status: string
  result: LearningState
  detail?: unknown
}

type AttemptResponse = {
  status: string
  mission_id: string
  result: LearningState
  detail?: unknown
}

export default function Mission() {
  const { missionId } = useParams()

  const [learningState, setLearningState] =
    useState<LearningState | null>(null)

  const [attempt, setAttempt] = useState('')

  const [evaluation, setEvaluation] =
    useState<Evaluation | null>(null)

  const [isLoadingMission, setIsLoadingMission] =
    useState(true)

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const [error, setError] = useState('')

  useEffect(() => {
    async function loadMission() {
      try {
        setIsLoadingMission(true)
        setError('')
        setAttempt('')
        setEvaluation(null)

        let data: StartLearningResponse

        const response = await fetch(
          'http://127.0.0.1:8080/api/learning/start',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              learner_id: 'demo-learner',
              skill: 'python',
              level: 'beginner',
              mission_id: missionId ?? undefined,
            }),
          },
        )

        data =
          (await response.json()) as StartLearningResponse

        if (!response.ok) {
          const detail = data.detail

          const message =
            typeof detail === 'string'
              ? detail
              : typeof detail === 'object' &&
                  detail !== null &&
                  'message' in detail
                ? String(
                    (
                      detail as {
                        message: unknown
                      }
                    ).message,
                  )
                : 'Unable to load the learning mission.'

          throw new Error(message)
        }

        if (!data.result) {
          throw new Error(
            'The learning service returned no mission.',
          )
        }

        setLearningState(data.result)
        setEvaluation(data.result.evaluation ?? null)
      } catch (missionError) {
        console.error(
          'Failed to load mission:',
          missionError,
        )

        setError(
          missionError instanceof Error
            ? missionError.message
            : 'Unable to load your mission.',
        )
      } finally {
        setIsLoadingMission(false)
      }
    }

    loadMission()
  }, [missionId])

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const trimmedAttempt = attempt.trim()

    const currentMission =
      learningState?.mission

    if (
      !trimmedAttempt ||
      isSubmitting ||
      !currentMission
    ) {
      return
    }

    setIsSubmitting(true)
    setError('')
    setEvaluation(null)

    try {
      const response = await fetch(
        `http://127.0.0.1:8080/api/missions/${
          missionId ?? '1'
        }/attempt`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            learner_id: 'demo-learner',
            skill: learningState.skill,
            level: learningState.level,
            mission: currentMission.title,
            attempt: trimmedAttempt,
            attempt_type: 'code',
          }),
        },
      )

      const data =
        (await response.json()) as AttemptResponse

      console.log(
        'Submission response status:',
        response.status,
      )

      console.log(
        'Submission response content-type:',
        response.headers.get('content-type'),
      )

      console.log(
        'Submission response body:',
        JSON.stringify(data, null, 2),
      )

      if (!response.ok) {
        const detail = data.detail

        const message =
          typeof detail === 'string'
            ? detail
            : typeof detail === 'object' &&
                detail !== null &&
                'message' in detail
              ? String(
                  (
                    detail as {
                      message: unknown
                    }
                  ).message,
                )
              : 'The learning evaluation failed.'

        throw new Error(message)
      }

      if (!data.result) {
        throw new Error(
          'The learning service returned no evaluation result.',
        )
      }

      setLearningState(data.result)
      setEvaluation(data.result.evaluation ?? null)
    } catch (submissionError) {
      console.error(
        'Submission failed:',
        submissionError,
      )

      setError(
        submissionError instanceof Error
          ? submissionError.message
          : 'Something went wrong while submitting your attempt.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const mission =
    learningState?.mission ?? null

  const missionSkills =
    mission?.skills ?? []

  const evaluationCriteria =
    evaluation?.criteria ?? []

  const evaluationStrengths =
    evaluation?.strengths ?? []

  const evaluationWeaknesses =
    evaluation?.weaknesses ?? []

  const learnerWeaknesses =
    learningState?.weaknesses ?? []

  const adaptedMission =
    learningState?.adapted_mission ?? null

  const adaptedExercise =
    adaptedMission?.targeted_exercise?.exercise ?? null

  const nextMission =
    adaptedMission?.next_mission ?? null

  const isMastered =
    evaluation?.passed === true &&
    (
      adaptedMission?.next_action ===
        'create_advanced_mission' ||
      adaptedMission?.next_action ===
        'learning_path_complete'
    )

  const learningLoopStatus =
    isMastered
      ? 'Mastery demonstrated'
      : adaptedExercise
        ? 'Targeted practice ready'
        : evaluation
          ? 'Evaluation complete'
          : 'Mission in progress'

  return (
    <main className="mission-page">
      <nav className="mission-nav">
        <Link to="/dashboard">
          ← Back to dashboard
        </Link>

        <span>
          Mission {missionId ?? '1'}
        </span>
      </nav>

      {isLoadingMission && (
        <section className="mission-header">
          <span className="eyebrow">
            PRACTICAL MISSION
          </span>

          <h1>
            Loading your mission...
          </h1>

          <p>
            Preparing your next hands-on challenge.
          </p>
        </section>
      )}

      {error && !mission && (
        <section className="mission-header">
          <span className="eyebrow">
            MISSION UNAVAILABLE
          </span>

          <h1>
            We couldn't load your mission.
          </h1>

          <p>{error}</p>

          <p>
            Make sure the MCP server and learning API
            are running.
          </p>
        </section>
      )}

      {!isLoadingMission && mission && (
        <>
          <section
            className="learning-loop"
            aria-label="Learning progress"
          >
            <div className="learning-loop-heading">
              <span className="eyebrow">
                YOUR LEARNING LOOP
              </span>

              <span>
                {learningLoopStatus}
              </span>
            </div>

            <div className="learning-loop-steps">
              <div className="learning-step active">
                <span>01</span>
                <strong>MISSION</strong>
              </div>

              <div className="learning-step active">
                <span>02</span>
                <strong>BUILD</strong>
              </div>

              <div
                className={`learning-step ${
                  evaluation ? 'active' : ''
                }`}
              >
                <span>03</span>
                <strong>EVALUATE</strong>
              </div>

              <div
                className={`learning-step ${
                  adaptedExercise || isMastered
                    ? 'active'
                    : ''
                }`}
              >
                <span>04</span>
                <strong>ADAPT</strong>
              </div>

              <div
                className={`learning-step ${
                  isMastered ? 'active' : ''
                }`}
              >
                <span>05</span>
                <strong>MASTER</strong>
              </div>
            </div>
          </section>

          <section className="mission-header">
            <span className="eyebrow">
              PRACTICAL MISSION
            </span>

            <h1>{mission.title}</h1>

            <p>
              Complete this practical challenge to
              continue your mastery journey. Your work
              will become the basis for the next
              evaluation and challenge.
            </p>
          </section>

          <section className="mission-content">
            <article className="mission-card">
              <div className="card-header">
                <div>
                  <span className="eyebrow">
                    YOUR CHALLENGE
                  </span>

                  <h2>{mission.title}</h2>
                </div>

                <span className="status">
                  ACTIVE
                </span>
              </div>

              <p>
                {mission.description}
              </p>

              {missionSkills.length > 0 && (
                <>
                  <h3>
                    Skills to practice
                  </h3>

                  <ul>
                    {missionSkills.map(
                      (skill) => (
                        <li key={skill}>
                          {skill}
                        </li>
                      ),
                    )}
                  </ul>
                </>
              )}

              <h3>
                What you need to prove
              </h3>

              <p>
                Don't just explain what you would
                build. Show what you actually built
                and provide enough evidence for the
                evaluator to assess your work.
              </p>
            </article>

            <form
              className="submission-card"
              onSubmit={handleSubmit}
            >
              <div>
                <span className="eyebrow">
                  YOUR ATTEMPT
                </span>

                <h2>
                  Show what you built
                </h2>

                <p>
                  Submit your implementation,
                  relevant evidence, and explain
                  how your solution demonstrates
                  the required skills.
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
                placeholder="Describe what you built and provide evidence of your implementation..."
                rows={12}
                required
              />

              <div className="submission-footer">
                <span>
                  {attempt.length} characters
                </span>

                <button
                  type="submit"
                  disabled={
                    !attempt.trim() ||
                    isSubmitting
                  }
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
                  <strong>
                    Evaluation failed
                  </strong>

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
                      <strong>
                        {evaluation.score}
                      </strong>

                      <span>/100</span>
                    </div>
                  </div>

                  {evaluationCriteria.length > 0 && (
                    <div className="criteria-list">
                      <h3>
                        What you proved
                      </h3>

                      {evaluationCriteria.map(
                        (criterion) => (
                          <article
                            className="criterion"
                            key={criterion.id}
                          >
                            <div className="criterion-header">
                              <strong>
                                {criterion.name}
                              </strong>

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

                            <p>
                              {criterion.evidence}
                            </p>
                          </article>
                        ),
                      )}
                    </div>
                  )}

                  {evaluationStrengths.length > 0 && (
                    <div className="evaluation-section">
                      <h3>
                        Strengths
                      </h3>

                      <ul>
                        {evaluationStrengths.map(
                          (
                            strength,
                            index,
                          ) => (
                            <li key={index}>
                              {strength}
                            </li>
                          ),
                        )}
                      </ul>
                    </div>
                  )}

                  {evaluationWeaknesses.length > 0 && (
                    <div className="evaluation-section">
                      <h3>
                        Areas to improve
                      </h3>

                      <ul>
                        {evaluationWeaknesses.map(
                          (
                            weakness,
                            index,
                          ) => (
                            <li key={index}>
                              {weakness}
                            </li>
                          ),
                        )}
                      </ul>
                    </div>
                  )}

                  <div className="evaluation-section">
                    <h3>
                      Feedback
                    </h3>

                    <p>
                      {evaluation.feedback}
                    </p>
                  </div>

                  {isMastered && nextMission && (
                    <section className="adapted-mission">
                      <div className="adapted-mission-header">
                        <div>
                          <span className="eyebrow">
                            NEXT MISSION
                          </span>

                          <h2>
                            {nextMission.title}
                          </h2>
                        </div>

                        <span className="status">
                          READY
                        </span>
                      </div>

                      <h3>
                        What you'll build
                      </h3>

                      <p>
                        {nextMission.description}
                      </p>

                      {nextMission.skills.length > 0 && (
                        <>
                          <h3>
                            Skills to practice
                          </h3>

                          <ul>
                            {nextMission.skills.map(
                              (skill) => (
                                <li key={skill}>
                                  {skill}
                                </li>
                              ),
                            )}
                          </ul>
                        </>
                      )}

                      {adaptedMission.message && (
                        <p>
                          {adaptedMission.message}
                        </p>
                      )}

                      <div className="next-action">
                        <span className="eyebrow">
                          MASTERY PROGRESSION
                        </span>

                        <h3>
                          You mastered this mission.
                          Your next challenge is ready.
                        </h3>

                        <Link
                          to={`/mission/${nextMission.id}`}
                          className="next-mission-button"
                        >
                          Start Next Mission →
                        </Link>
                      </div>
                    </section>
                  )}

                  {learnerWeaknesses.length > 0 && (
                    <div className="evaluation-section">
                      <h3>
                        Targeted practice
                      </h3>

                      <p>
                        Your next challenge has
                        been adapted to focus on
                        the areas you need to
                        strengthen.
                      </p>
                    </div>
                  )}

                  {adaptedExercise && (
                    <section className="adapted-mission">
                      <div className="adapted-mission-header">
                        <div>
                          <span className="eyebrow">
                            ADAPTED NEXT CHALLENGE
                          </span>

                          <h2>
                            {adaptedExercise.title}
                          </h2>
                        </div>

                        <span className="status">
                          READY
                        </span>
                      </div>

                      <h3>
                        Objective
                      </h3>

                      <p>
                        {adaptedExercise.objective}
                      </p>

                      {adaptedExercise.instructions?.length > 0 && (
                        <>
                          <h3>
                            What to do
                          </h3>

                          <ol>
                            {adaptedExercise.instructions.map(
                              (
                                instruction,
                                index,
                              ) => (
                                <li key={index}>
                                  {instruction}
                                </li>
                              ),
                            )}
                          </ol>
                        </>
                      )}

                      <h3>
                        Success signal
                      </h3>

                      <p>
                        {adaptedExercise.success_signal}
                      </p>

                      <div className="next-action">
                        <span className="eyebrow">
                          LEARNING LOOP
                        </span>

                        <h3>
                          Complete this challenge,
                          submit your attempt, and
                          evaluate the new attempt.
                        </h3>
                      </div>
                    </section>
                  )}
                </section>
              )}
            </form>
          </section>
        </>
      )}
    </main>
  )
}
