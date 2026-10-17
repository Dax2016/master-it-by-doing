import { Fragment, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'


function renderBossFightInline(text: string) {
  const parts = text.split(/(\*\*.+?\*\*|`[^`]+`|\*[^*\n]+\*)/g)

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>
    }

    if (part.startsWith("`") && part.endsWith("`")) {
      return <code className="boss-fight-inline-code" key={index}>{part.slice(1, -1)}</code>
    }

    if (part.startsWith("*") && part.endsWith("*")) {
      return <em key={index}>{part.slice(1, -1)}</em>
    }

    return <Fragment key={index}>{part}</Fragment>
  })
}

function BossFightMessage({ content }: { content?: string }) {
  const normalized = (content ?? "").replace(/\\([`*_#>~])/g, "$1")
  const lines = normalized.replace(/\r\n?/g, "\n").split("\n")
  const blocks = []
  let index = 0

  const isBlockStart = (line: string) =>
    /^#{1,3}\s+/.test(line) ||
    /^>\s?/.test(line) ||
    /^[-*+]\s+/.test(line) ||
    /^\d+[.)]\s+/.test(line)

  while (index < lines.length) {
    const line = lines[index].trim()

    if (!line) {
      index += 1
      continue
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/)
    if (heading) {
      blocks.push(
        <h3 key={`heading-${index}`}>{renderBossFightInline(heading[2])}</h3>,
      )
      index += 1
      continue
    }

    if (/^>\s?/.test(line)) {
      const quoteLines = []
      while (index < lines.length && /^>\s?/.test(lines[index].trim())) {
        quoteLines.push(lines[index].trim().replace(/^>\s?/, ""))
        index += 1
      }
      blocks.push(
        <blockquote key={`quote-${index}`}>
          {quoteLines.map((quote, quoteIndex) => (
            <p key={quoteIndex}>{renderBossFightInline(quote)}</p>
          ))}
        </blockquote>,
      )
      continue
    }

    const unordered = /^[-*+]\s+/.test(line)
    const ordered = /^\d+[.)]\s+/.test(line)

    if (unordered || ordered) {
      const items = []
      const pattern = unordered ? /^[-*+]\s+/ : /^\d+[.)]\s+/

      while (index < lines.length && pattern.test(lines[index].trim())) {
        items.push(lines[index].trim().replace(pattern, ""))
        index += 1
      }

      const ListTag = ordered ? "ol" : "ul"
      blocks.push(
        <ListTag key={`list-${index}`}>
          {items.map((item, itemIndex) => (
            <li key={itemIndex}>{renderBossFightInline(item)}</li>
          ))}
        </ListTag>,
      )
      continue
    }

    const paragraph = [line]
    index += 1

    while (
      index < lines.length &&
      lines[index].trim() &&
      !isBlockStart(lines[index].trim())
    ) {
      paragraph.push(lines[index].trim())
      index += 1
    }

    blocks.push(
      <p key={`paragraph-${index}`}>
        {renderBossFightInline(paragraph.join(" "))}
      </p>,
    )
  }

  return <div className="boss-fight-markdown">{blocks}</div>
}

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
  interview_transcript?: {
    role?: string
    content?: string
    attempt_type?: string
    timestamp?: string
  }[]
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
  examiner_message?: string
  turn_count?: number
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
  const navigate = useNavigate()

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
  const [isActivatingNextMission, setIsActivatingNextMission] =
    useState(false)
  const [nextMissionError, setNextMissionError] = useState('')

  async function handleStartNextMission(nextMission: NextMission) {
    if (isActivatingNextMission) return

    setIsActivatingNextMission(true)
    setNextMissionError('')

    try {
      const response = await fetch(
        `http://127.0.0.1:8001/api/missions/${encodeURIComponent(nextMission.id)}/activate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            learner_id: learningState?.learner_id ?? 'demo-learner',
            skill: nextMission.skill,
            level: learningState?.level ?? 'beginner',
          }),
        },
      )

      const result = await response.json().catch(() => null)

      if (!response.ok) {
        const detail = result?.detail
        throw new Error(
          typeof detail === 'string'
            ? detail
            : 'Could not activate the next mission. Please try again.',
        )
      }

      navigate(`/mission/${encodeURIComponent(nextMission.id)}`)
    } catch (err) {
      setNextMissionError(
        err instanceof Error
          ? err.message
          : 'Could not activate the next mission. Please try again.',
      )
    } finally {
      setIsActivatingNextMission(false)
    }
  }

  const [bossFight, setBossFight] =
    useState<BossFightChallenge | null>(null)
  const [bossFightResponse, setBossFightResponse] = useState('')
  const [bossFightDraft, setBossFightDraft] = useState('')
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
        setBossFightDraft('')
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
    setBossFightDraft('')

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

      // Preserve the started challenge even if the opening question fails.
      setBossFight(payload.challenge)

      const interview = await requestBossFight(
        `/api/boss-fights/${encodeURIComponent(bossFight.id)}/interview`,
        'POST',
        {
          ...bossFightBasePayload(),
          learner_response: '',
          attempt_type: bossFightAttemptType,
        },
      )

      if (!interview.challenge || !interview.examiner_message) {
        const backendMessage =
          typeof interview.message === 'string' ? interview.message : undefined
        throw new Error(
          backendMessage ??
          'The examiner response was incomplete. Check the API terminal for details.',
        )
      }

      setBossFight(interview.challenge)
      setBossFightDraft('')
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

  const continueBossFightInterview = async () => {
    if (!mission || !bossFight || bossFightBusy) return

    const hasTranscript = (bossFight.interview_transcript?.length ?? 0) > 0
    const answer = bossFightDraft.trim()

    // An empty answer is permitted only to retry the opening question.
    if (hasTranscript && !answer) return

    setBossFightBusy(true)
    setBossFightError('')

    try {
      const payload = await requestBossFight(
        `/api/boss-fights/${encodeURIComponent(bossFight.id)}/interview`,
        'POST',
        {
          ...bossFightBasePayload(),
          learner_response: answer,
          attempt_type: bossFightAttemptType,
        },
      )

      if (!payload.challenge || !payload.examiner_message) {
        const backendMessage =
          typeof payload.message === 'string' ? payload.message : undefined
        throw new Error(
          backendMessage ??
          'The examiner response was incomplete. Check the API terminal for details.',
        )
      }

      setBossFight(payload.challenge)
      setBossFightDraft('')
    } catch (requestError) {
      setBossFightError(
        requestError instanceof Error
          ? requestError.message
          : 'Could not continue the interview.',
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

          <section className="mission-header mission-header--visual">
            <div className="mission-header-copy">
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
            </div>

            <div className="mission-visual">
              <img
                src="/images/mission/mission-practical-visual-ms_03.jpg"
                alt="Visual inspiration for your practical learning mission"
                loading="lazy"
              />
              <span className="mission-visual-caption">
                LEARN BY BUILDING
              </span>
            </div>
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

                        {nextMissionError && (
                          <p role="alert" className="error-message">
                            {nextMissionError}
                          </p>
                        )}

                        <button
                          type="button"
                          className="next-mission-button"
                          onClick={() => handleStartNextMission(nextMission)}
                          disabled={isActivatingNextMission}
                        >
                          {isActivatingNextMission
                            ? 'Activating Mission...'
                            : 'Start Next Mission →'}
                        </button>
                      </div>
                    </section>
                  )}

                  {isMastered &&
                    !nextMission &&
                    adaptedMission?.next_action === 'learning_path_complete' && (
                      <section className="adapted-mission">
                        <div className="adapted-mission-header">
                          <div>
                            <span className="eyebrow">SKILL PATH COMPLETE</span>
                            <h2>Learning Path Complete!</h2>
                          </div>
                          <span className="status">MASTERED</span>
                        </div>
                        <p>
                          {adaptedMission.message ??
                            'You have completed every mission in this skill path. You can now demonstrate your skills in a Boss Fight assessment or build a portfolio project.'}
                        </p>
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
          <div className="boss-fight-examiner-bar">
            <div className="boss-fight-examiner-mark" aria-hidden="true">B</div>
            <div className="boss-fight-examiner-copy">
              <span className="boss-fight-examiner-kicker">MASTER IT BY DOING · MASTERY INTERVIEW</span>
              <strong>The Technical Examiner</strong>
              <span>Practical reasoning, implementation and evidence</span>
            </div>
            <div className="boss-fight-live-indicator">
              <span aria-hidden="true" />
              {bossFight?.status === 'in_progress'
                ? 'SESSION LIVE'
                : bossFight?.status === 'ready'
                  ? 'READY WHEN YOU ARE'
                  : 'ASSESSMENT SPACE'}
            </div>
          </div>
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
              <div className="boss-fight-conversation-intro">
                <span className="boss-fight-conversation-avatar" aria-hidden="true">TE</span>
                <div>
                  <span className="boss-fight-label">LIVE TECHNICAL INTERVIEW</span>
                  <p>
                    Think aloud, explain trade-offs, and respond to follow-up
                    questions. Your final implementation is submitted separately
                    for evaluation.
                  </p>
                </div>
              </div>

              <div className="boss-fight-chat-heading">
                <div>
                  <span className="boss-fight-label">EXAMINER SESSION</span>
                  <h3>Reason it through.</h3>
                </div>
                <span className="boss-fight-turn-count">
                  {(bossFight.interview_transcript ?? []).filter(
                    (turn) => turn.role === 'learner',
                  ).length} answers
                </span>
              </div>

              <div
                className="boss-fight-chat-log"
                aria-label="Boss Fight interview transcript"
                aria-live="polite"
              >
                {!(bossFight.interview_transcript?.length) ? (
                  <div className="boss-fight-chat-empty">
                    <span className="boss-fight-chat-empty-mark" aria-hidden="true">B</span>
                    <strong>Your examiner is ready.</strong>
                    <p>
                      Request the opening question to begin your conversation.
                    </p>
                    <button
                      type="button"
                      className="boss-fight-secondary"
                      onClick={continueBossFightInterview}
                      disabled={bossFightBusy}
                    >
                      {bossFightBusy ? 'Connecting?' : 'Get opening question'}
                    </button>
                  </div>
                ) : (
                  bossFight.interview_transcript.map((turn, index) => (
                    <article
                      className={`boss-fight-chat-message ${
                        turn.role === 'learner'
                          ? 'boss-fight-chat-message-learner'
                          : 'boss-fight-chat-message-examiner'
                      }`}
                      key={`${turn.timestamp ?? 'turn'}-${index}`}
                    >
                      <span className="boss-fight-chat-role">
                        {turn.role === 'learner' ? 'YOU' : 'THE TECHNICAL EXAMINER'}
                      </span>
                      <BossFightMessage content={turn.content} />
                    </article>
                  ))
                )}
                {bossFightBusy && (
                  <div className="boss-fight-thinking" role="status">
                    <span />
                    <span />
                    <span />
                    <p>The examiner is considering your response?</p>
                  </div>
                )}
              </div>

              <div className="boss-fight-chat-composer">
                <label htmlFor="boss-fight-draft">Your response to the examiner</label>
                <textarea
                  id="boss-fight-draft"
                  value={bossFightDraft}
                  onChange={(event) => setBossFightDraft(event.target.value)}
                  placeholder="Explain your reasoning, answer the question, or discuss a trade-off?"
                  rows={4}
                  disabled={bossFightBusy}
                />
                <div className="boss-fight-composer-actions">
                  <span>Be specific. The examiner may ask you to go deeper.</span>
                  <button
                    type="button"
                    className="boss-fight-primary"
                    onClick={continueBossFightInterview}
                    disabled={
                      bossFightBusy ||
                      !(bossFight.interview_transcript?.length) ||
                      !bossFightDraft.trim()
                    }
                  >
                    {bossFightBusy ? 'Thinking?' : 'Send response'}
                  </button>
                </div>
              </div>

              <div className="boss-fight-final-evidence">
                <div className="boss-fight-final-evidence-heading">
                  <span className="boss-fight-label">FINAL SUBMISSION</span>
                  <h3>Show the work.</h3>
                  <p>
                    When you are ready, provide the implementation or written
                    evidence that should be assessed. Interview messages alone
                    are not treated as your final solution.
                  </p>
                </div>

                <label htmlFor="boss-fight-attempt-type">Evidence format</label>
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
                  placeholder="Paste your final code or explain the completed solution, including key decisions and results."
                  rows={9}
                  disabled={bossFightBusy}
                />

                <button
                  type="button"
                  className="boss-fight-primary"
                  onClick={evaluateBossFight}
                  disabled={bossFightBusy || !bossFightResponse.trim()}
                >
                  {bossFightBusy ? 'Evaluating?' : 'Finish Interview & Evaluate'}
                </button>
              </div>
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
