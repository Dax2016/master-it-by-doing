import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface MissionDetails {
  id: string
  title: string
  description: string
  skills: string[]
}

interface LearnerRecord {
  learner_id: string
  goals: Record<string, unknown>[]
  completed_missions: Record<string, unknown>[]
  attempts: Record<string, unknown>[]
  evidence: Record<string, unknown>[]
  capabilities: Record<string, unknown>[]
  strengths: string[]
  weaknesses: string[]
  mastery: Record<string, Record<string, Record<string, unknown>>>
}

interface CapabilityProfile {
  status: string
  learner_id: string
  capabilities: Record<string, unknown>[]
}

interface LearningStateResponse {
  status: string
  learner_id: string
  skill: string
  level: string
  state: {
    status: string
    learner: LearnerRecord
  }
  capabilities: CapabilityProfile
}

interface LearningState {
  learner_id: string
  skill: string
  level: string
  goal: Record<string, unknown> | null
  mission: MissionDetails | null
  latest_attempt: Record<string, unknown> | null
  attempt_text: string | null
  attempt_type: string
  evaluation: Record<string, unknown> | null
  weaknesses: string[] | null
  targeted_exercise: Record<string, unknown> | null
  adapted_mission: Record<string, unknown> | null
  next_action: string
}

interface StartLearningResponse {
  status: string
  result: LearningState
}

const API_BASE_URL = 'http://127.0.0.1:8080'

export default function Dashboard() {
  const [learningState, setLearningState] =
    useState<LearningState | null>(null)

  const [learnerProfile, setLearnerProfile] =
    useState<LearnerProfile | null>(null)

  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadLearningState() {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(
          `${API_BASE_URL}/api/learning/state?learner_id=demo-learner&skill=python&level=beginner`,
        )

        if (!response.ok) {
          throw new Error(
            `Learning service returned HTTP ${response.status}`,
          )
        }

        const data: LearningStateResponse =
          await response.json()

        const profileResponse = await fetch(
          `${API_BASE_URL}/api/learning/profile?learner_id=demo-learner&skill=python&level=beginner`,
        )

        if (!profileResponse.ok) {
          throw new Error(
            `Learner profile service returned HTTP ${profileResponse.status}`,
          )
        }

        const profileData: LearningProfileResponse =
          await profileResponse.json()

        if (!profileData.profile) {
          throw new Error(
            'Learning service returned no learner profile.',
          )
        }

        setLearnerProfile(profileData.profile)

        const learner = data.state?.learner

        if (!learner) {
          throw new Error(
            'Learning service returned no learner state.',
          )
        }

        const goals = learner.goals ?? []
        const attempts = learner.attempts ?? []
        const weaknesses = learner.weaknesses ?? []

        setLearningState({
          learner_id: learner.learner_id,
          skill: data.skill,
          level: data.level,
          goal: goals.length > 0
            ? goals[goals.length - 1]
            : null,
          mission: null,
          latest_attempt:
            attempts.length > 0
              ? attempts[attempts.length - 1]
              : null,
          attempt_text: null,
          attempt_type: 'code',
          evaluation: null,
          weaknesses,
          targeted_exercise: null,
          adapted_mission: null,
          next_action:
            goals.length === 0
              ? 'create_learning_goal'
              : 'continue_learning',
        })
      } catch (err) {
        console.error(
          'Failed to load learner state:',
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

    loadLearningState()
  }, [])

  async function startLearningJourney() {
    try {
      setStarting(true)
      setError(null)

      const response = await fetch(
        `${API_BASE_URL}/api/learning/start`,
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

      const data: StartLearningResponse =
        await response.json()

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
          : 'Unable to start your learning journey.',
      )
    } finally {
      setStarting(false)
    }
  }

  const hasGoal =
    learningState?.goal !== null &&
    learningState?.goal !== undefined

  const activeMission =
    learnerProfile?.current?.active_mission

  const activeMissionId =
    typeof activeMission?.mission_id === 'string'
      ? activeMission.mission_id
      : null

  const activeMissionTitle =
    typeof activeMission?.title === 'string'
      ? activeMission.title
      : 'Your practical challenge'

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
              Checking your current mastery state.
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
          <>
            {!hasGoal ? (
              <div className="dashboard-card">
                <span>Ready to begin</span>

                <h2>
                  Start your practical learning journey
                </h2>

                <p>
                  Master It By Doing turns your learning
                  goal into practical missions. You build,
                  submit your work, prove what you know, and
                  receive the next challenge based on your
                  demonstrated ability.
                </p>

                <button
                  type="button"
                  className="primary-btn"
                  onClick={startLearningJourney}
                  disabled={starting}
                >
                  {starting
                    ? 'Creating your mission...'
                    : 'Start learning ?'}
                </button>
              </div>
            ) : (
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
                    {typeof learningState.goal?.message ===
                    'string'
                      ? learningState.goal.message
                      : 'Build practical skills through hands-on challenges.'}
                  </p>
                </div>

                <div className="dashboard-card">
                  <span>Learning status</span>

                  <strong className="big-score">
                    {learningState.next_action ===
                    'submit_attempt'
                      ? 'Mission ready'
                      : 'Learning in progress'}
                  </strong>

                  <p>
                    Continue building practical evidence
                    toward mastery.
                  </p>
                </div>

                <div className="dashboard-card mission-dashboard-card">
                  <span>Current mission</span>

                  <h2>
                    {activeMissionTitle}
                  </h2>

                  <p>
                    {typeof activeMission?.description ===
                    'string'
                      ? activeMission.description
                      : 'Your active mission is available from your learning journey.'}
                  </p>

                  {activeMissionId ? (
                    <Link
                      to={`/mission/${activeMissionId}`}
                      className="primary-btn"
                    >
                      Continue mission ?
                    </Link>
                  ) : (
                    <span className="primary-btn">
                      No active mission
                    </span>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </section>
    </main>
  )
}
interface LearnerProfile {
  learner_id: string
  current: {
    goal: Record<string, unknown> | null
    active_mission: Record<string, unknown> | null
  }
  demonstrated: {
    capabilities: Record<string, unknown>[]
    completed_missions: Record<string, unknown>[]
    evidence_count: number
  }
  mastery: {
    mastered: Record<string, unknown>[]
    developing: Record<string, unknown>[]
    needs_practice: Record<string, unknown>[]
  }
  strengths: string[]
  weaknesses: string[]
  next: {
    mission: Record<string, unknown> | null
  }
}

interface LearningProfileResponse {
  status: string
  learner_id: string
  skill: string
  level: string
  profile: LearnerProfile
}





