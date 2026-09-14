import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

interface MissionDetails {
  title: string
  description: string
  skills: string[]
}

interface MissionResponse {
  status: string
  skill: string
  learner_level: string
  mission: MissionDetails
  next_action: string
}

interface LearningState {
  learner_id: string
  skill: string
  level: string
  goal: Record<string, unknown> | null
  mission: MissionResponse | null
  latest_attempt: unknown
  attempt_text: string | null
  attempt_type: string
  evaluation: unknown
  weaknesses: string[] | null
  targeted_exercise: unknown
  adapted_mission: unknown
  next_action: string
}

interface StartLearningResponse {
  status: string
  result: LearningState
}

export default function Dashboard() {
  const [learningState, setLearningState] =
    useState<LearningState | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const startedRef = useRef(false)

  useEffect(() => {
    if (startedRef.current) {
      return
    }

    startedRef.current = true

    async function startLearningJourney() {
      try {
        setLoading(true)
        setError(null)

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
            }),
          },
        )

        if (!response.ok) {
          throw new Error(
            `Learning service returned HTTP ${response.status}`,
          )
        }

        const data: StartLearningResponse = await response.json()

        if (!data.result) {
          throw new Error(
            'Learning service returned no learning state.',
          )
        }

        setLearningState(data.result)
      } catch (err) {
        console.error(
          'Failed to start learning journey:',
          err,
        )

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load your learning journey.',
        )
      } finally {
        setLoading(false)
      }
    }

    startLearningJourney()
  }, [])

  const mission = learningState?.mission?.mission

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div className="brand">
          <img
            src="/brand/master-it-by-doing.png"
            alt="Master It By Doing"
            className="brand-logo"
          />

          <span>Master It By Doing</span>
        </div>

        <button>Sign out</button>
      </header>

      <section className="dashboard-content">
        <div>
          <span className="eyebrow">
            YOUR MASTERY JOURNEY
          </span>

          <h1>Welcome back.</h1>

          <p>
            Your next challenge is waiting for you.
          </p>
        </div>

        {loading && (
          <div className="dashboard-card">
            <span>
              Loading your learning journey...
            </span>

            <p>
              Creating your practical mission.
            </p>
          </div>
        )}

        {error && (
          <div className="dashboard-card">
            <span>
              Unable to load your journey
            </span>

            <p>{error}</p>

            <p>
              Make sure the learning API is running on
              http://127.0.0.1:8080.
            </p>
          </div>
        )}

        {!loading && !error && learningState && (
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <span>Current goal</span>

              <h2>
                {learningState.skill
                  ? learningState.skill
                      .charAt(0)
                      .toUpperCase() +
                    learningState.skill.slice(1)
                  : 'Learning goal'}
              </h2>

              <p>
                {learningState.goal &&
                typeof learningState.goal.message ===
                  'string'
                  ? learningState.goal.message
                  : 'Build practical skills through hands-on challenges.'}
              </p>
            </div>

            <div className="dashboard-card">
              <span>Learning status</span>

              <strong className="big-score">
                Mission ready
              </strong>

              <p>
                Complete the practical mission to continue
                your mastery journey.
              </p>
            </div>

            <div className="dashboard-card mission-dashboard-card">
              <span>Current mission</span>

              <h2>
                {mission?.title ??
                  'No mission available'}
              </h2>

              <p>
                {mission?.description ??
                  'Your next practical challenge will appear here.'}
              </p>

              {mission?.skills &&
                mission.skills.length > 0 && (
                  <div>
                    <span>Skills to practice</span>

                    <ul>
                      {mission.skills.map((skill) => (
                        <li key={skill}>
                          {skill}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

              {mission && (
                <Link
                  to="/mission/1"
                  className="primary-btn"
                >
                  Continue mission →
                </Link>
              )}
            </div>
          </div>
        )}
      </section>
    </main>
  )
}