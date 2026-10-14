import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'

interface MissionDetails {
  id: string
  title: string
  description: string
  skills: string[]
}

interface LearnerRecord {
  learner_id: string
  active_mission?: Record<string, unknown> | null
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
  active_mission?: Record<string, unknown> | null
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

interface LearningPath {
  skill: string
  id: string
  title: string
  difficulty: string
  description: string
  mission_count: number
}

interface LearningPathsResponse {
  status: string
  paths: LearningPath[]
}
interface StartLearningResponse {
  status: string
  result: LearningState
}

const API_BASE_URL = 'http://127.0.0.1:8001'

export default function Dashboard() {
  const [learningState, setLearningState] =
    useState<LearningState | null>(null)

  const [learnerProfile, setLearnerProfile] =
    useState<LearnerProfile | null>(null)

  const [learningPaths, setLearningPaths] =
    useState<LearningPath[]>([])

  const [evidenceRecords, setEvidenceRecords] =
    useState<Record<string, unknown>[]>([])

  const [selectedPath, setSelectedPath] =
    useState('python')

  const initialPathResolved = useRef(false)


  const [pathsLoading, setPathsLoading] = useState(true)
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    let cancelled = false

    async function loadLearningState() {
      try {
        setLoading(true)
        setError(null)
        const pathsResponse = await fetch(
          `${API_BASE_URL}/api/learning/paths`,
        )

        if (!pathsResponse.ok) {
          throw new Error(
            `Learning paths service returned HTTP ${pathsResponse.status}`,
          )
        }

        const pathsData: LearningPathsResponse =
          await pathsResponse.json()

        const availablePaths = pathsData.paths ?? []
        setLearningPaths(availablePaths)
        setPathsLoading(false)

        if (!initialPathResolved.current) {
          const profileResponse = await fetch(
            `${API_BASE_URL}/api/learning/profile?learner_id=demo-learner&all_skills=true`,
            { signal: controller.signal },
          )

          if (!profileResponse.ok) {
            throw new Error(
              `Learner profile service returned HTTP ${profileResponse.status}`,
            )
          }

          const initialProfileData: LearningProfileResponse =
            await profileResponse.json()

          const savedGoalSkill =
            initialProfileData.profile?.current?.goal?.skill

          const savedGoalPath =
            typeof savedGoalSkill === 'string'
              ? availablePaths.find(
                  (path) => path.skill === savedGoalSkill,
                )
              : undefined

          initialPathResolved.current = true

          if (savedGoalPath && savedGoalPath.skill !== selectedPath) {
            setSelectedPath(savedGoalPath.skill)
            return
          }
        }

        const response = await fetch(
          `${API_BASE_URL}/api/learning/state?learner_id=demo-learner&skill=${encodeURIComponent(selectedPath)}&level=beginner`,
          { signal: controller.signal },
        )

        if (!response.ok) {
          throw new Error(
            `Learning service returned HTTP ${response.status}`,
          )
        }

        const data: LearningStateResponse =
          await response.json()

        const profileResponse = await fetch(
          `${API_BASE_URL}/api/learning/profile?learner_id=demo-learner&skill=${encodeURIComponent(selectedPath)}&level=beginner`,
          { signal: controller.signal },
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

        if (cancelled) return

        setLearnerProfile(profileData.profile)

        const learner = data.state?.learner

        if (!learner) {
          throw new Error(
            'Learning service returned no learner state.',
          )
        }

        const goals = Array.isArray(learner.goals)
          ? learner.goals
          : []
        const attempts = learner.attempts ?? []
        const weaknesses = learner.weaknesses ?? []

        const normalizeSkillKey = (value: unknown) =>
          typeof value === 'string'
            ? value.trim().toLowerCase().replace(/[_\s]+/g, '-')
            : ''

        const evidence = Array.isArray(learner.evidence)
          ? learner.evidence
          : []

        setEvidenceRecords(
          evidence.filter(
            (record) =>
              normalizeSkillKey(record?.skill) ===
              normalizeSkillKey(selectedPath),
          ),
        )

        const matchingGoal = [...goals].reverse().find(
          (goal) =>
            normalizeSkillKey(goal?.skill) ===
              normalizeSkillKey(selectedPath) &&
            normalizeSkillKey(goal?.learner_level) === 'beginner',
        )

        const selectedGoal =
          profileData.profile.current?.goal ?? matchingGoal ?? null

        setLearningState({
          learner_id: learner.learner_id,
          skill: data.skill,
          level: data.level,
          goal: selectedGoal,
          active_mission: learner.active_mission ?? null,
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
        if (cancelled) return

        if (err instanceof DOMException && err.name === 'AbortError') {
          return
        }

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
        if (!cancelled) setLoading(false)
      }
    }

    void loadLearningState()

    return () => {
      cancelled = true
      controller.abort()
    }
  }, [selectedPath])

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
            skill: selectedPath,
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

      // Refresh the profile after the learning cycle creates its mission.
      const profileResponse = await fetch(
        `${API_BASE_URL}/api/learning/profile?learner_id=demo-learner&skill=${encodeURIComponent(selectedPath)}&level=beginner`,
      )

      if (profileResponse.ok) {
        const profileData: LearningProfileResponse =
          await profileResponse.json()

        if (profileData.profile) {
          setLearnerProfile(profileData.profile)
        }
      } else {
        console.error(
          'Learning started, but the profile refresh failed:',
          profileResponse.status,
        )
      }
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

  const stateGoalSkill = learningState?.goal?.skill
  const profileGoalSkill = learnerProfile?.current?.goal?.skill

  const currentGoalSkill =
    typeof stateGoalSkill === 'string'
      ? stateGoalSkill
      : typeof profileGoalSkill === 'string'
        ? profileGoalSkill
        : learningState?.skill

  const normalizeSkill = (value: unknown): string =>
    typeof value === 'string'
      ? value.trim().toLowerCase().replace(/[_\s]+/g, '-')
      : ''

  const selectedSkillKey = normalizeSkill(selectedPath)

  const skillAchievements = (
    learnerProfile?.achievements ?? []
  ).filter(
    (achievement) =>
      normalizeSkill(achievement.skill) === selectedSkillKey,
  )
  const missionsBySkill = learnerProfile?.current?.active_missions
  const skillMission = missionsBySkill?.[selectedSkillKey] ?? null

  const profileActiveMission =
    learnerProfile?.current?.active_mission

  const stateActiveMission = learningState?.active_mission

  const activeMissionCandidate =
    skillMission ??
    (normalizeSkill(profileActiveMission?.skill) === selectedSkillKey
      ? profileActiveMission
      : null) ??
    (normalizeSkill(stateActiveMission?.skill) === selectedSkillKey
      ? stateActiveMission
      : null)

  const activeMission = activeMissionCandidate

  const completedMissionsForSkill = (
  learnerProfile?.demonstrated?.completed_missions ?? []
  ).filter(
  (mission) =>
    normalizeSkill(mission.skill) === selectedSkillKey,
  )


const learningStatus =
    learningState?.next_action === 'submit_attempt'
      ? 'Mission ready'
      : activeMission
        ? 'Learning in progress'
        : completedMissionsForSkill.length > 0
          ? 'Mission mastered'
          : learningState?.next_action === 'create_learning_goal'
            ? 'Set your learning goal'
            : 'Ready to begin'



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

<div className="dashboard-hero">
  <div className="dashboard-hero-copy">
    <span className="eyebrow">
      YOUR MASTERY JOURNEY
    </span>

    <h1>Welcome back.</h1>

    <p>
      Your next challenge is waiting for you.
    </p>

    <p className="dashboard-hero-tagline">
      Learn. Build. Prove. Advance.
    </p>
  </div>

  <img
    src="/images/dashboard/ms_04.jpg"
    alt="Master It By Doing learning journey"
    className="dashboard-hero-image"
  />
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
              http://127.0.0.1:8001.
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
              <>
                <div className="dashboard-grid">
                <div className="dashboard-card">
                  <span>Current goal</span>

                  <h2>
                    {currentGoalSkill
                      ? currentGoalSkill.charAt(0).toUpperCase() +
                        currentGoalSkill.slice(1)
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
                {learningStatus}
              </strong>


                  <p>
                    Continue building practical evidence
                    toward mastery.
                  </p>
                </div>


<div className="dashboard-card mission-dashboard-card">
  <span>Current mission</span>

  <img
    src="/images/dashboard/ms_05.jpg"
    className="mission-dashboard-image"
  />

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

              <section className="evidence-portfolio-section achievements-section">
                <div className="evidence-portfolio-header">
                  <div>
                    <span className="eyebrow">
                      SKILL MILESTONES
                    </span>
                    <h2>Your Achievements</h2>
                    <p>
                      Badges earned through demonstrated progress in this learning path.
                    </p>
                  </div>
                  <strong className="evidence-count">
                    {skillAchievements.length} {skillAchievements.length === 1 ? 'badge' : 'badges'}
                  </strong>
                </div>

                {skillAchievements.length === 0 ? (
                  <div className="dashboard-card evidence-empty-state achievements-empty-state">
                    <h3>Your first badge awaits</h3>
                    <p>
                      Complete an eligible challenge successfully to earn an achievement for this skill.
                    </p>
                  </div>
                ) : (
                  <div className="evidence-grid">
                    {skillAchievements.map((achievement, index) => {
                      const title =
                        typeof achievement.title === 'string'
                          ? achievement.title
                          : typeof achievement.name === 'string'
                            ? achievement.name
                            : typeof achievement.achievement_id === 'string'
                              ? achievement.achievement_id
                              : 'Achievement'

                      const description =
                        typeof achievement.description === 'string'
                          ? achievement.description
                          : typeof achievement.boss_fight_id === 'string'
                            ? `Earned by passing Boss Fight ${achievement.boss_fight_id}.`
                            : 'Achievement earned for this learning path.'

                      const recordKey =
                        typeof achievement.id === 'string'
                          ? achievement.id
                          : typeof achievement.achievement_id === 'string'
                            ? achievement.achievement_id
                            : `${title}-${index}`

                      return (
                        <article
                          className="evidence-card achievement-card"
                          key={recordKey}
                        >
                      <div className="evidence-card-topline">
                      <span className="evidence-source">
                     {String.fromCodePoint(0x1F3C6)} {title}
                   </span>
              </div>
                          <h3>{title}</h3>
                          <p>{description}</p>
                          {typeof achievement.skill === 'string' && (
                            <span className="evidence-status passed">
                              {achievement.skill}
                            </span>
                          )}
                        </article>
                      )
                    })}
                  </div>
                )}
              </section>

              <section className="evidence-portfolio-section">
                <div className="evidence-portfolio-header">
                  <div>
                    <span className="eyebrow">
                      PROOF OF PROGRESS
                    </span>
                    <h2>Your Evidence Portfolio</h2>
                    <p>
                      Evaluated work and demonstrated results for this learning path.
                    </p>
                  </div>
                  <strong className="evidence-count">
                    {evidenceRecords.length} {evidenceRecords.length === 1 ? 'record' : 'records'}
                  </strong>
                </div>

                {evidenceRecords.length === 0 ? (
                  <div className="dashboard-card evidence-empty-state">
                    <h3>No evidence recorded yet</h3>
                    <p>
                      Complete and submit a mission or evaluate a Boss Fight to build your portfolio for this skill.
                    </p>
                  </div>
                ) : (
                  <div className="evidence-grid">
                    {evidenceRecords.map((record, index) => {
                      const title =
                        typeof record.mission === 'string'
                          ? record.mission
                          : typeof record.mission_id === 'string'
                            ? record.mission_id
                            : 'Practical evidence'
                      const score =
                        typeof record.score === 'number'
                          ? record.score
                          : null
                      const passed =
                        record.passed === true
                          ? 'Passed'
                          : record.passed === false
                            ? 'Needs more practice'
                            : 'Result unavailable'
                      const statusClass =
                        record.passed === true
                          ? 'passed'
                          : record.passed === false
                            ? 'needs-practice'
                            : 'unknown'
                      const passedCriteria =
                        typeof record.passed_criteria === 'number'
                          ? record.passed_criteria
                          : null
                      const totalCriteria =
                        typeof record.total_criteria === 'number'
                          ? record.total_criteria
                          : null
                      const feedback =
                        typeof record.feedback === 'string'
                          ? record.feedback
                          : ''
                      const sourceLabel =
                        record.evidence_type === 'boss_fight'
                          ? 'Boss Fight'
                          : 'Mission evidence'
                      const recordKey =
                        typeof record.id === 'string'
                          ? record.id
                          : `${title}-${index}`

                      return (
                        <article className="evidence-card" key={recordKey}>
                          <div className="evidence-card-topline">
                            <span className="evidence-source">
                              {sourceLabel}
                            </span>
                            <span className={`evidence-status ${statusClass}`}>
                              {passed}
                            </span>
                          </div>

                          <h3>{title}</h3>

                          <div className="evidence-result-row">
                            <div>
                              <span className="evidence-label">Score</span>
                              <strong className="evidence-score">
                                {score !== null ? `${score}%` : '?'}
                              </strong>
                            </div>
                            {passedCriteria !== null && totalCriteria !== null && (
                              <div>
                                <span className="evidence-label">Criteria met</span>
                                <strong className="evidence-criteria">
                                  {passedCriteria} / {totalCriteria}
                                </strong>
                              </div>
                            )}
                          </div>

                          {feedback && (
                            <p className="evidence-feedback">
                              {feedback}
                            </p>
                          )}
                        </article>
                      )
                    })}
                  </div>
                )}
              </section>

              <section className="learning-paths-section">
                <div>
                  <span className="eyebrow">
                    AVAILABLE CAPABILITIES
                  </span>

                  <h2>Choose what to master next.</h2>

                  <p>
                    Build practical evidence across different
                    learning paths.
                  </p>
                </div>

                {pathsLoading ? (
                  <div className="dashboard-card">
                    <span>Loading learning paths...</span>
                  </div>
                ) : learningPaths.length === 0 ? (
                  <div className="dashboard-card">
                    <span>No learning paths available.</span>
                  </div>
                ) : (
                  <div className="dashboard-grid">
                {learningPaths.map((path) => (
                 <button
                 key={path.skill}
                 type="button"
                 className={`dashboard-card learning-path-card ${
                 selectedPath === path.skill ? 'selected' : ''
            }`}
             onClick={() => setSelectedPath(path.skill)}
            aria-pressed={selectedPath === path.skill}
  >
      <span>{path.difficulty}</span>

    <h2>{path.title}</h2>

    <p>{path.description}</p>

    <p>
      {path.mission_count} practical{' '}
      {path.mission_count === 1
        ? 'mission'
        : 'missions'}
    </p>

    <strong>
      {selectedPath === path.skill
        ? 'Selected'
        : 'Select path'}
    </strong>
  </button>
  ))}
                  </div>
                )}
              </section>
              </>
            )}

          </>
        )}
      </section>
    </main>
  )
}
interface LearnerProfile {
  learner_id: string
  achievements?: Record<string, unknown>[]
  current: {
    goal: Record<string, unknown> | null
    active_mission: Record<string, unknown> | null
    active_missions?: Record<string, Record<string, unknown>>
    active_practices?: Record<string, Record<string, unknown>>
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
