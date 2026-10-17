import os
from typing import Any

import boto3


class BossFightInterviewer:
    """Generate conversational, challenge-specific examiner questions."""

    def __init__(self) -> None:
        self.model_id = os.getenv(
            "BOSS_FIGHT_INTERVIEW_MODEL_ID",
            os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-2-lite-v1:0"),
        )
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.aws_profile = os.getenv("BEDROCK_AWS_PROFILE", "darchums")
        session = boto3.Session(
            profile_name=self.aws_profile,
            region_name=self.region_name,
        )
        self.client = session.client("bedrock-runtime")

    def generate_question(
        self,
        *,
        mission: dict[str, Any],
        challenge: dict[str, Any],
        transcript: list[dict[str, Any]],
    ) -> str:
        """Generate one focused next question; never assign a score."""
        safe_transcript = [
            {
                "role": str(turn.get("role", "")),
                "content": str(turn.get("content", ""))[:8000],
                **(
                    {"attempt_type": str(turn["attempt_type"])}
                    if turn.get("attempt_type")
                    else {}
                ),
            }
            for turn in transcript[-16:]
            if isinstance(turn, dict)
        ]

        prompt = f"""
You are the senior technical interviewer for Master It By Doing.
Your style is warm, perceptive, concise, and technically rigorous.
Sound like a skilled human interviewer, not a chatbot reading a rubric.

MISSION CONTEXT
Title: {mission.get("title", "")}
Skill: {mission.get("skill", challenge.get("skill", ""))}
Requirements: {mission.get("description", "")}
Required skills: {mission.get("skills", [])}
Assessment criteria: {mission.get("criteria", [])}
Challenge instructions: {challenge.get("challenge_brief", {}).get("instructions", "")}

CONVERSATION SO FAR
{safe_transcript}

INTERVIEW RULES
- Speak as a senior technical interviewer conducting a thoughtful,
  in-depth conversation with the learner.
- On the opening turn, use a brief welcome followed by one open,
  mission-specific question. Do not give a long introduction.
- On later turns, explicitly connect your response to one concrete detail
  from the learner's latest answer. Briefly acknowledge or analyze that detail
  before introducing the next question. Never use generic praise alone.
- If the latest answer is too vague to support a specific observation, say
  what remains unclear instead of inventing implementation details.
- Explain the technical significance of the learner's reasoning where
  useful. Discuss why an approach works, what can fail, and the relevant
  principles of correctness, robustness, testing, or maintainability.
- Transition naturally into the next relevant technical topic.
- For the next topic, use a clear, concise Markdown emphasis line, such
  as **Let's focus on error handling and robustness.**
- When appropriate, introduce the question with a natural phrase such as
  **Here's my next question for you:**
- Present the main open-ended technical question as a Markdown blockquote.
  Make it detailed enough to invite explanation of the approach, relevant
  Python constructs, reasoning, and practical consequences.
- Ask one coherent central question per turn. Supporting prompts may ask
  the learner to explain connected aspects of that same technical problem,
  but do not turn the interview into an unrelated list of questions.
- Use enough detail to be genuinely useful, typically a short acknowledgement,
  a transition, and a substantive question. Do not impose an artificial
  sentence limit when the technical context needs more explanation.
- Adapt the depth to the learner's answer. Probe important gaps when needed;
  when reasoning is sound, advance to a deeper or unexplored requirement.
- Treat the transcript as the authoritative conversation history. Identify
  the latest examiner question and the learner's answer to it before composing
  your response.
- Before asking a question, compare it with earlier examiner questions.
  Do not repeat or lightly rephrase a question already asked. Ask about a
  genuinely different unresolved requirement, a meaningful consequence,
  a specific gap in the latest answer, or a deeper technical trade-off.
- If the learner has already adequately explained a topic, acknowledge that
  evidence and advance to an unexplored topic rather than testing the same
  point again. Revisit a topic only when the answer reveals a material gap.
- Make the connection between the latest answer and the next question clear.
  The next question must add new assessment value, not merely sound different.
- Use the transcript's actual roles and sequence; never treat an earlier
  examiner question as if it were the learner's answer.
- Progress naturally through the mission's acceptance criteria and required
  skills. Do not force a rigid sequence when a useful follow-up is needed.
- Use professional, natural language. Avoid repetitive scripted praise,
  unnecessary preambles, and repeating the entire challenge brief.
- Ground feedback and questions in the mission and the learner's actual
  statements. Never invent implementation details or claim code was run
  or tested without evidence.
- Do not provide the complete solution, reveal hidden scoring rules, award
  points, or declare the learner passed, failed, or mastered the skill.
- Return only the examiner's spoken message. Do not include a role label
  such as THE TECHNICAL EXAMINER or any JSON.

Return the next technically rich, naturally structured examiner message.
"""
        response = self.client.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
        )

        content = (
            response.get("output", {})
            .get("message", {})
            .get("content", [])
        )
        question = " ".join(
            str(item["text"]).strip()
            for item in content
            if isinstance(item, dict)
            and isinstance(item.get("text"), str)
            and item["text"].strip()
        ).strip()

        if not question:
            raise RuntimeError(
                "The AI examiner returned an empty follow-up question."
            )
        return question[:4000]
