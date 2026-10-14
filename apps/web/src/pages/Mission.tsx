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

type AttemptResponse = {
  status: string
  mission_id: string
  result: LearningState
  detail?: unknown
}


type BossFightChallenge = {
  id: string
  status: string
  parent_mission_title?: string
  evaluation?: Record<string, unknown> | null
  challenge_brief?: {
    instructions?: string
    skills?: string[]
    criteria?: { id?: string; name?: string }[]
  }
}

type BossFightApiResponse = {
  status?: string
  challenge?: BossFightChallenge
  evaluation?: Record<string, unknown>
  detail?: unknown
  message?: string
}

type VoiceReaction = {
  emoji: string
  title: string
  message: string
}


type VoiceProfile = {
  id: string
  name: string
  description: string
  gender: 'male' | 'female'
  character: string
  rate: number
  pitch: number
}

const VOICE_PROFILES: VoiceProfile[] = [
  {
    id: 'mentor',
    name: 'The Mentor',
    description: 'Calm, clear and thoughtful',
    gender: 'male',
    character: 'White male character',
    rate: 0.95,
    pitch: 0.95,
  },
  {
    id: 'coach',
    name: 'The Coach',
    description: 'Energetic and motivating',
    gender: 'male',
    character: 'Black male character',
    rate: 1.05,
    pitch: 1.05,
  },
  {
    id: 'guide',
    name: 'The Guide',
    description: 'Patient and reassuring',
    gender: 'female',
    character: 'White female character',
    rate: 0.95,
    pitch: 1.08,
  },
  {
    id: 'challenger',
    name: 'The Challenger',
    description: 'Expressive and confident',
    gender: 'female',
    character: 'Black female character',
    rate: 1.05,
    pitch: 1.12,
  },
]


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

  const [bossFight, setBossFight] =
    useState<BossFightChallenge | null>(null)
  const [bossFightResponse, setBossFightResponse] = useState('')
  const [bossFightEvaluation, setBossFightEvaluation] =
    useState<Record<string, unknown> | null>(null)
  const [bossFightBusy, setBossFightBusy] = useState(false)
  const [bossFightError, setBossFightError] = useState('')
  const [bossFightAttemptType, setBossFightAttemptType] =
    useState<'code' | 'text' | 'answer'>('code')

  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [voiceReaction, setVoiceReaction] =
  useState<VoiceReaction | null>(null)

  
  const [selectedVoice, setSelectedVoice] = useState<string>(() => {
  if (typeof window === 'undefined') return 'default'

  return window.localStorage.getItem(
    'master-it-by-doing-voice-profile',
  ) || 'default'
})

useEffect(() => {
  window.localStorage.setItem(
    'master-it-by-doing-voice-profile',
    selectedVoice,
  )
}, [selectedVoice])


function speakWithProfile(
  message: string,
  profileId: string,
) {
  if (
    typeof window === 'undefined' ||
    !('speechSynthesis' in window)
  ) {
    return
  }

  const synth = window.speechSynthesis

  const preferredVoiceNames: Record<string, string[]> = {
    mentor: [
      'Microsoft George - English (United Kingdom)',
      'Microsoft Luke Online (Natural) - English (South Africa)',
      'Microsoft Thomas Online (Natural) - English (United Kingdom)',
    ],
    coach: [
      'Microsoft Ryan Online (Natural) - English (United Kingdom)',
      'Microsoft Luke Online (Natural) - English (South Africa)',
      'Microsoft Andrew Online (Natural) - English (United States)',
    ],
    guide: [
      'Microsoft Sonia Online (Natural) - English (United Kingdom)',
      'Microsoft Leah Online (Natural) - English (South Africa)',
      'Microsoft Hazel - English (United Kingdom)',
    ],
    challenger: [
      'Microsoft Natasha Online (Natural) - English (Australia)',
      'Microsoft Leah Online (Natural) - English (South Africa)',
      'Microsoft Emma Online (Natural) - English (United States)',
    ],
  }

  const profile = VOICE_PROFILES.find(
    (item) => item.id === profileId,
  )

  function speak(voices: SpeechSynthesisVoice[]) {
    const utterance = new SpeechSynthesisUtterance(message)

    utterance.lang = 'en'
    utterance.rate = profile?.rate ?? 1
    utterance.pitch = profile?.pitch ?? 1.05
    utterance.volume = 1

    if (profile) {
      const names = preferredVoiceNames[profile.id] ?? []

      const matchingVoice = names
        .map((name) => voices.find((voice) => voice.name === name))
        .find(
          (voice): voice is SpeechSynthesisVoice =>
            voice !== undefined,
        )

      if (matchingVoice) {
        utterance.voice = matchingVoice
        utterance.lang = matchingVoice.lang
      } else {
        const englishVoice = voices.find((voice) =>
          voice.lang.toLowerCase().startsWith('en'),
        )

        if (englishVoice) {
          utterance.voice = englishVoice
          utterance.lang = englishVoice.lang
        }
      }
    }

    synth.cancel()
    synth.speak(utterance)
  }

  let attempts = 0

  function waitForVoices() {
    const voices = synth.getVoices()

    if (voices.length > 0 || attempts >= 4) {
      speak(voices)
      return
    }

    attempts += 1
    window.setTimeout(waitForVoices, 250)
  }

  waitForVoices()
}
function announceReaction(reaction: VoiceReaction) {
  setVoiceReaction(reaction)

  if (!voiceEnabled) return

  speakWithProfile(reaction.message, selectedVoice)
}

  useEffect(() => {
    async function loadMission() {
      try {
        setIsLoadingMission(true)
        setError('')
        setAttempt('')
        setEvaluation(null)
        setBossFight(null)
        setBossFightResponse('')
        setBossFightEvaluation(null)
        setBossFightError('')
        setBossFightAttemptType('code')

        if (!missionId) {
          throw new Error(
            'No mission ID was provided.',
          )
        }

        const response = await fetch(
          `http://127.0.0.1:8001/api/missions/${missionId}`,
        )

        const data =
          (await response.json()) as MissionResponse & {
            status: string
            mission_id: string
            detail?: unknown
            criteria?: Criterion[]
            concept_id?: string
          }

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

        if (!data.mission_id) {
          throw new Error(
            'The learning service returned no mission ID.',
          )
        }

        const mission: MissionResponse = {
          mission: data.mission,
          skill: data.skill,
          id: data.mission_id,
          title: data.title,
          description: data.description,
          skills: data.skills,
        }

        const nextLearningState: LearningState = {
          learner_id: 'demo-learner',
          skill: data.skill,
          level: 'beginner',
          goal: null,
          mission,
          latest_attempt: null,
          attempt_text: null,
          attempt_type: 'code',
          evaluation: null,
          weaknesses: null,
          targeted_exercise: null,
          adapted_mission: null,
          next_action: 'submit_attempt',
        }

        setLearningState(nextLearningState)
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
        `http://127.0.0.1:8001/api/missions/${
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

const resultEvaluation =
  data.result.evaluation ?? null

setEvaluation(resultEvaluation)

const nextAction =
  data.result.adapted_mission?.next_action

let reaction: VoiceReaction

if (
  resultEvaluation?.passed === true &&
  (
    nextAction === 'create_advanced_mission' ||
    nextAction === 'learning_path_complete'
  )
) {
  reaction = {
    emoji: '🏆',
    title: 'Mastery demonstrated!',
    message:
      "Outstanding! You've demonstrated mastery of this mission. Your hard work paid off!",
  }
} else if (
  resultEvaluation?.passed === true &&
  nextAction === 'retry_parent_mission'
) {
  reaction = {
    emoji: '🎯',
    title: 'Targeted practice completed!',
    message:
      "Excellent! You've strengthened the skill you were working on. Now let's apply it to the original mission!",
  }
} else if (resultEvaluation?.passed === true) {
  reaction = {
    emoji: '🎉',
    title: 'Great work!',
    message:
      "Well done! You've passed this evaluation. Keep building and strengthening your skills!",
  }
} else if (resultEvaluation) {
  reaction = {
    emoji: '💪',
    title: 'Keep going!',
    message:
      "Not quite yet, but every attempt is progress. Let's work on the areas that need improvement and try again!",
  }
} else {
  reaction = {
    emoji: '🔎',
    title: 'Submission received',
    message:
      "Your submission has been received. Let's review the results and see what you've demonstrated!",
  }
}

announceReaction(reaction)
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

  const practiceCompleted =
    adaptedMission?.next_action === 'retry_parent_mission'

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
      : practiceCompleted
        ? 'Practice complete — retry original mission'
        : adaptedExercise
          ? 'Targeted practice ready'
          : evaluation
            ? 'Evaluation complete'
            : 'Mission in progress'

  const bossFightBasePayload = () => ({
    learner_id: learningState?.learner_id ?? 'demo-learner',
    skill: mission?.skill ?? 'python',
    parent_mission_id: mission?.id ?? '',
  })

  const requestBossFight = async (
    path: string,
    method: 'GET' | 'POST',
    body?: Record<string, unknown>,
  ): Promise<BossFightApiResponse> => {
    const response = await fetch(
      `http://127.0.0.1:8001${path}`,
      {
        method,
        headers: { 'Content-Type': 'application/json' },
        ...(body ? { body: JSON.stringify(body) } : {}),
      },
    )

    const payload = await response.json() as BossFightApiResponse

    if (!response.ok) {
      const detail = payload.detail
      const message =
        typeof detail === 'string'
          ? detail
          : detail && typeof detail === 'object' &&
              'message' in detail &&
              typeof detail.message === 'string'
            ? detail.message
            : payload.message

      throw new Error(
        message ?? `Boss Fight request failed (${response.status}).`,
      )
    }

    return payload
  }

  const createBossFight = async () => {
    if (!mission || bossFightBusy) return

    setBossFightBusy(true)
    setBossFightError('')
    setBossFightEvaluation(null)
    setBossFightResponse('')

    try {
      const payload = await requestBossFight(
        '/api/boss-fights',
        'POST',
        bossFightBasePayload(),
      )

      if (!payload.challenge) {
        throw new Error('The server did not return a Boss Fight challenge.')
      }

      setBossFight(payload.challenge)
    } catch (requestError) {
      setBossFightError(
        requestError instanceof Error
          ? requestError.message
          : 'Could not create the Boss Fight.',
      )
    } finally {
      setBossFightBusy(false)
    }
  }

  const startBossFight = async () => {
    if (!mission || !bossFight || bossFightBusy) return

    setBossFightBusy(true)
    setBossFightError('')

    try {
      const payload = await requestBossFight(
        `/api/boss-fights/${encodeURIComponent(bossFight.id)}/start`,
        'POST',
        bossFightBasePayload(),
      )

      if (!payload.challenge) {
        throw new Error('The server did not return the started challenge.')
      }

      setBossFight(payload.challenge)
    } catch (requestError) {
      setBossFightError(
        requestError instanceof Error
          ? requestError.message
          : 'Could not start the Boss Fight.',
      )
    } finally {
      setBossFightBusy(false)
    }
  }

  const evaluateBossFight = async () => {
    if (
      !mission ||
      !bossFight ||
      !bossFightResponse.trim() ||
      bossFightBusy
    ) {
      return
    }

    setBossFightBusy(true)
    setBossFightError('')

    try {
      const payload = await requestBossFight(
        `/api/boss-fights/${encodeURIComponent(bossFight.id)}/evaluate`,
        'POST',
        {
          ...bossFightBasePayload(),
          learner_response: bossFightResponse.trim(),
          attempt_type: bossFightAttemptType,
        },
      )

      if (!payload.challenge || !payload.evaluation) {
        throw new Error('The server returned an incomplete evaluation.')
      }

      setBossFight(payload.challenge)
      setBossFightEvaluation(payload.evaluation)
    } catch (requestError) {
      setBossFightError(
        requestError instanceof Error
          ? requestError.message
          : 'Could not evaluate the Boss Fight.',
      )
    } finally {
      setBossFightBusy(false)
    }
  }

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
                  adaptedExercise || practiceCompleted || isMastered
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

          <section
  className="voice-companion"
  aria-live="polite"
>
  <div className="voice-companion-controls">
    <div>
      <span className="eyebrow">
        YOUR LEARNING COMPANION
      </span>
      <p>
        Encouragement that responds to your actual
        learning results.
      </p>
    </div>

    <button
      type="button"
      onClick={() => {
        if (voiceEnabled) {
          window.speechSynthesis?.cancel()
        }
        setVoiceEnabled((enabled) => !enabled)
      }}
      aria-pressed={voiceEnabled}
    >
      {voiceEnabled ? '🔊 Voice on' : '🔇 Voice off'}
    </button>
  </div>


  <div className="voice-profile-picker">
    <label htmlFor="learning-voice-profile">
      Choose your learning voice
    </label>

    <select
      id="learning-voice-profile"
      value={selectedVoice}
      onChange={(event) => setSelectedVoice(event.target.value)}
    >
      <option value="default">Existing voice (default)</option>
      {VOICE_PROFILES.map((profile) => (
        <option key={profile.id} value={profile.id}>
          {profile.name} — {profile.character}
        </option>
      ))}
    </select>

    {VOICE_PROFILES.map((profile) => (
      <div className="voice-profile-option" key={profile.id}>
        <div>
          <strong>{profile.name}</strong>
          <p>{profile.description}</p>
        </div>

        <button
          type="button"
          disabled={!voiceEnabled}
          onClick={() =>
            speakWithProfile(
              `Hello! I am ${profile.name}. ${profile.description}. Let's continue learning together.`,
              profile.id,
            )
          }
        >
          Preview voice
        </button>
      </div>
    ))}
  </div>

  {voiceReaction && (
    <div className="voice-reaction">
      <span
        className="voice-reaction-emoji"
        aria-hidden="true"
      >
        {voiceReaction.emoji}
      </span>

      <div>
        <h3>{voiceReaction.title}</h3>
        <p>{voiceReaction.message}</p>

        <button
          type="button"
          disabled={!voiceEnabled}
          onClick={() => {
            announceReaction(voiceReaction)
          }}
        >
          ▶ Replay reaction
        </button>
      </div>
    </div>
  )}
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
                          Start Next Mission â†’
                        </Link>
                      </div>
                    </section>
                  )}

                  {practiceCompleted && mission && (
                    <section className="adapted-mission">
                      <div className="adapted-mission-header">
                        <div>
                          <span className="eyebrow">
                            PRACTICE COMPLETE
                          </span>
                          <h2>
                            You're ready to retry the original mission.
                          </h2>
                        </div>
                        <span className="status">PASSED</span>
                      </div>

                      <p>
                        You've strengthened the skill identified in your
                        previous evaluation. Now apply it to the complete
                        {` ${mission.title}`} challenge.
                      </p>

                      {adaptedMission?.message && (
                        <p>{adaptedMission.message}</p>
                      )}

                      <div className="next-action">
                        <span className="eyebrow">YOUR NEXT STEP</span>
                        <h3>
                          Return to your original solution and demonstrate
                          the skill in context.
                        </h3>

                        <button
                          type="button"
                          className="next-mission-button"
                          onClick={() => {
                            setAttempt('')
                            setEvaluation(null)
                            setError('')

                            setLearningState((current) =>
                              current
                                ? {
                                    ...current,
                                    latest_attempt: null,
                                    attempt_text: null,
                                    evaluation: null,
                                    weaknesses: null,
                                    targeted_exercise: null,
                                    adapted_mission: null,
                                    next_action: 'submit_attempt',
                                  }
                                : current,
                            )
                          }}
                        >
                          Retry Original Mission →
                        </button>
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
      {!isLoadingMission && mission && (
        <section className="boss-fight-card" aria-labelledby="boss-fight-title">
          <div className="boss-fight-header">
            <div>
              <span className="boss-fight-eyebrow">INDEPENDENT SKILL CHECK</span>
              <h2 id="boss-fight-title">Boss Fight</h2>
              <p>
                Prove what you can do with a practical assessment based on
                your current mission. This assessment is tracked separately
                from your normal mission progress.
              </p>
            </div>
            {bossFight && (
              <span className={`boss-fight-status boss-fight-status-${bossFight.status}`}>
                {bossFight.status.replaceAll('_', ' ')}
              </span>
            )}
          </div>

          <div className="boss-fight-context">
            <span className="boss-fight-label">MISSION CONTEXT</span>
            <h3>{mission.title}</h3>
            <p>{mission.mission || mission.description}</p>
          </div>

          {bossFight?.challenge_brief && (
            <section className="boss-fight-brief" aria-labelledby="boss-fight-brief-title">
              <div className="boss-fight-brief-heading">
                <span className="boss-fight-label">CHALLENGE BRIEF</span>
                <span className="boss-fight-id">ID: {bossFight.id}</span>
              </div>

              <h3 id="boss-fight-brief-title">Your task</h3>
              <p className="boss-fight-brief-instructions">
                {bossFight.challenge_brief.instructions || 'Complete the mission challenge and demonstrate your solution.'}
              </p>

              {!!bossFight.challenge_brief.skills?.length && (
                <div className="boss-fight-brief-section">
                  <h4>Skills to demonstrate</h4>
                  <ul className="boss-fight-brief-skills">
                    {bossFight.challenge_brief.skills.map((skill) => (
                      <li key={skill}>{skill}</li>
                    ))}
                  </ul>
                </div>
              )}

              {!!bossFight.challenge_brief.criteria?.length && (
                <div className="boss-fight-brief-section">
                  <h4>Acceptance criteria</h4>
                  <ul className="boss-fight-brief-criteria">
                    {bossFight.challenge_brief.criteria.map((criterion, index) => (
                      <li key={criterion.id || `${criterion.name || 'criterion'}-${index}`}>
                        <span className="boss-fight-criterion-marker" aria-hidden="true">?</span>
                        <span>{criterion.name || criterion.id || 'Complete the required criterion'}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}

          {bossFightError && (
            <p className="boss-fight-error" role="alert">
              {bossFightError}
            </p>
          )}

          {!bossFight && (
            <button
              type="button"
              className="boss-fight-primary"
              onClick={createBossFight}
              disabled={bossFightBusy}
            >
              {bossFightBusy ? 'Preparing challenge…' : 'Create Boss Fight'}
            </button>
          )}

          {bossFight?.status === 'ready' && (
            <div className="boss-fight-actions">
              <p>Your challenge is ready. Start when you are prepared.</p>
              <button
                type="button"
                className="boss-fight-primary"
                onClick={startBossFight}
                disabled={bossFightBusy}
              >
                {bossFightBusy ? 'Starting…' : 'Start Challenge'}
              </button>
            </div>
          )}

          {bossFight?.status === 'in_progress' && (
            <div className="boss-fight-workspace">
              <label htmlFor="boss-fight-attempt-type">Submission type</label>
              <select
                id="boss-fight-attempt-type"
                value={bossFightAttemptType}
                onChange={(event) => setBossFightAttemptType(
                  event.target.value as 'code' | 'text' | 'answer',
                )}
                disabled={bossFightBusy}
              >
                <option value="code">Code / implementation</option>
                <option value="text">Written explanation</option>
                <option value="answer">Short answer</option>
              </select>

              <label htmlFor="boss-fight-response">Your solution and evidence</label>
              <textarea
                id="boss-fight-response"
                value={bossFightResponse}
                onChange={(event) => setBossFightResponse(event.target.value)}
                placeholder="Describe or paste your solution. Include enough detail to demonstrate your reasoning and the result."
                rows={9}
                disabled={bossFightBusy}
              />

              <button
                type="button"
                className="boss-fight-primary"
                onClick={evaluateBossFight}
                disabled={bossFightBusy || !bossFightResponse.trim()}
              >
                {bossFightBusy ? 'Evaluating…' : 'Submit for Evaluation'}
              </button>
            </div>
          )}

          {bossFightEvaluation && (
            <div className="boss-fight-result" aria-live="polite">
              <div className="boss-fight-score">
                <span className="boss-fight-label">YOUR SCORE</span>
                <strong>
                  {typeof bossFightEvaluation.score === 'number'
                    ? `${bossFightEvaluation.score}%`
                    : 'Evaluated'}
                </strong>
                <span>
                  {bossFightEvaluation.passed === true
                    ? 'Challenge passed'
                    : bossFightEvaluation.passed === false
                      ? 'More practice needed'
                      : 'Evaluation complete'}
                </span>
              </div>

              {typeof bossFightEvaluation.feedback === 'string' && (
                <p>{bossFightEvaluation.feedback}</p>
              )}

              {Array.isArray(bossFightEvaluation.strengths) &&
                bossFightEvaluation.strengths.some(
                  (item) => typeof item === 'string',
                ) && (
                  <div>
                    <h3>What you did well</h3>
                    <ul>
                      {bossFightEvaluation.strengths.map((item, index) =>
                        typeof item === 'string'
                          ? <li key={index}>{item}</li>
                          : null,
                      )}
                    </ul>
                  </div>
                )}

              {Array.isArray(bossFightEvaluation.weaknesses) &&
                bossFightEvaluation.weaknesses.some(
                  (item) => typeof item === 'string',
                ) && (
                  <div>
                    <h3>Areas to strengthen</h3>
                    <ul>
                      {bossFightEvaluation.weaknesses.map((item, index) =>
                        typeof item === 'string'
                          ? <li key={index}>{item}</li>
                          : null,
                      )}
                    </ul>
                  </div>
                )}

              <p className="boss-fight-note">
                This result is recorded independently. Your parent mission
                status has not been automatically changed.
              </p>
            </div>
          )}

          {(bossFight?.status === 'passed' || bossFight?.status === 'failed') && (
            <button
              type="button"
              className="boss-fight-secondary"
              onClick={createBossFight}
              disabled={bossFightBusy}
            >
              {bossFightBusy ? 'Preparing…' : 'Try a New Boss Fight'}
            </button>
          )}
        </section>
      )}

    </main>
  )
}
