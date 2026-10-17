import os
import uuid
from copy import deepcopy

from services.assessment.assessment_service import AssessmentService
from services.assessment.boss_fight_engine import BossFightEngine
from services.assessment.boss_fight_interviewer import BossFightInterviewer
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from services.learner.learner_state import LearnerState
from content.course_catalog import (
    get_concept_for_mission,
    get_concepts_for_mission,
    get_concepts as get_catalog_concepts,
    get_missions,
    get_mission_by_id,
)


allowed_hosts = [
    host.strip()
    for host in os.getenv("MCP_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# Keep local development secure when no hosts are configured.
if not allowed_hosts:
    allowed_hosts = [
        "127.0.0.1:*",
        "localhost:*",
]


mcp = FastMCP(
    "Master It By Doing",
    transport_security=TransportSecuritySettings(
        allowed_hosts=allowed_hosts,
    ),
)

app = mcp.streamable_http_app()
learners: dict[str, LearnerState] = {}


def get_learner(
    learner_id: str = "demo-learner",
) -> LearnerState:
    """Return the isolated learner state for a learner ID."""

    normalized_id = learner_id.strip() or "demo-learner"

    if normalized_id not in learners:
        learners[normalized_id] = LearnerState(
            learner_id=normalized_id,
        )

    return learners[normalized_id]

# AI evidence collection plus deterministic mission validation.
assessment_service = AssessmentService()

boss_fight_engine = BossFightEngine()
boss_fight_interviewer = BossFightInterviewer()


# ---------------------------------------------------------------------------
# MISSION RESOLUTION
# ---------------------------------------------------------------------------

def resolve_mission(
    skill: str,
    mission: str,
) -> dict:
    """
    Resolve a learner-facing mission string into the canonical
    mission definition used by the assessment and Ground Truth layers.
    """

    normalized_skill = skill.strip().lower()
    normalized_mission = mission.strip().lower()

    canonical_missions = get_missions(
        normalized_skill,
    )

    for canonical in canonical_missions:
        canonical_title = canonical["title"].strip().lower()
        canonical_id = str(canonical.get("id", "")).strip().lower()

        if (
            normalized_mission == canonical_id
            or normalized_mission == canonical_title
            or normalized_mission.startswith(
                canonical_title + ":"
            )
            or canonical_title in normalized_mission
        ):
            return {
                "id": canonical["id"],
                "skill": skill,
                "title": canonical["title"],
                "mission": canonical["title"],
                "description": canonical["description"],
                "skills": canonical["skills"],
                "criteria": canonical.get("criteria", []),
            }

    # Fallback for unknown missions.
    #
    # We intentionally preserve the supplied mission rather than
    # inventing requirements.
    return {
        "skill": skill,
        "title": mission,
        "mission": mission,
        "skills": [],
    }


# ---------------------------------------------------------------------------
# LEARNING GOAL
# ---------------------------------------------------------------------------

@mcp.tool()
def create_learning_goal(
    skill: str,
    learner_level: str = "beginner",
    learner_id: str = "demo-learner",
    practice: bool = False,
) -> dict:
    """
    Create and record a practical learning goal for the learner.

    Repeated requests for the same learner, skill, and level are
    idempotent and do not create duplicate goals.
    """

    learner = get_learner(learner_id)

    existing_goal = next(
        (
            goal
            for goal in learner.goals
            if goal.get("skill") == skill
            and goal.get("learner_level") == learner_level
        ),
        None,
    )

    if existing_goal is not None:
        return {
            "status": "exists",
            "learner_id": learner.learner_id,
            "skill": skill,
            "learner_level": learner_level,
            "goal": existing_goal,
            "message": (
                f"Learning goal already exists: learn {skill} "
                f"at {learner_level} level."
            ),
            "next_action": "Continue with the learner's active mission.",
        }

    goal = {
        "skill": skill,
        "learner_level": learner_level,
    }

    learner.add_goal(goal)

    return {
        "status": "created",
        "learner_id": learner.learner_id,
        "skill": skill,
        "learner_level": learner_level,
        "goal": goal,
        "message": (
            f"Learning goal created: learn {skill} "
            f"at {learner_level} level."
        ),
        "next_action": "Create a practical learning mission.",
    }


# ---------------------------------------------------------------------------
# CONCEPT DISCOVERY
# ---------------------------------------------------------------------------

@mcp.tool()
def get_concepts(
    skill: str,
) -> dict:
    """
    Return the learning concepts available for a skill.
    """

    concepts = get_catalog_concepts(skill)

    return {
        "skill": skill,
        "concepts": concepts,
    }


# MISSION ACTIVATION
# ---------------------------------------------------------------------------

def normalize_skill_name(skill: str) -> str:
    return skill.strip().casefold().replace("_", "-").replace(" ", "-")


@mcp.tool()
def activate_mission(
    mission_id: str,
    skill: str,
    learner_id: str = "demo-learner",
) -> dict:
    """Activate one exact catalog mission without replacing active work."""

    lookup = get_mission_by_id(mission_id.strip())
    if lookup is None:
        return {
            "status": "not_found",
            "message": f"Unknown mission ID: {mission_id}",
        }

    canonical_skill, mission = lookup
    if normalize_skill_name(skill) != normalize_skill_name(canonical_skill):
        return {
            "status": "skill_mismatch",
            "message": "The mission does not belong to the requested skill.",
        }

    learner = get_learner(learner_id)
    active = learner.get_active_mission(canonical_skill)

    if active and active.get("status") == "in_progress":
        if active.get("mission_id") == mission.get("id"):
            return {
                "status": "resumed",
                "learner_id": learner.learner_id,
                "skill": canonical_skill,
                "mission": mission,
            }

        return {
            "status": "conflict",
            "message": "Another mission is already in progress for this skill.",
            "active_mission": active,
        }

    learner.set_active_mission(mission, canonical_skill)
    return {
        "status": "activated",
        "learner_id": learner.learner_id,
        "skill": canonical_skill,
        "mission": mission,
    }


# MISSION CREATION
# ---------------------------------------------------------------------------

@mcp.tool()
def create_mission(
    skill: str,
    learner_level: str = "beginner",
    concept_id: str | None = None,
    learner_id: str = "demo-learner",
    practice: bool = False,
) -> dict:
    """
    Create or resume a practical hands-on learning mission.

    If the learner already has an active mission for the requested skill,
    return that mission instead of creating or replacing it.
    """

    learner = get_learner(learner_id)

    # -----------------------------------------------------------------------
    # Resume an existing active mission.
    # -----------------------------------------------------------------------

    active_mission = learner.get_active_mission(skill)

    if (
        active_mission is not None
        and active_mission.get("status") == "in_progress"
        and active_mission.get("skill") == skill
        and concept_id is None
    ):
        return {
            "status": "resumed",
            "learner_id": learner.learner_id,
            "skill": skill,
            "learner_level": learner_level,
            "mission": active_mission,
            "next_action": (
                "Continue the active mission."
            ),
        }

    # -----------------------------------------------------------------------
    # Select a new mission.
    # -----------------------------------------------------------------------

    missions = get_missions(
        skill,
    )

    if concept_id:
        mission = next(
            (
                candidate
                for candidate in missions
                if concept_id in [
                    concept.get("id")
                    for concept in get_catalog_concepts(skill)
                    if candidate.get("id")
                    in concept.get("mission_ids", [])
                ]
            ),
            None,
        )
    else:
        mastered_missions = {
            mission_title
            for mission_title, result in learner.mastery.get(
                skill,
                {},
            ).items()
            if result.get("status") == "mastered"
            and result.get("passed") is True
        }

        mission = next(
            (
                candidate
                for candidate in missions
                if candidate.get("title") not in mastered_missions
            ),
            None,
        )

    if mission is None:
        mission = {
            "title": f"Build a Practical {skill.title()} Project",
            "description": (
                f"Complete a small hands-on project that demonstrates "
                f"fundamental {skill} skills at the {learner_level} level."
            ),
            "skills": [
                f"Fundamentals of {skill.title()}",
                "Problem solving",
                "Practical implementation",
            ],
        }

    learner.set_active_mission(mission, skill)

    return {
        "status": "created",
        "learner_id": learner.learner_id,
        "skill": skill,
        "learner_level": learner_level,
        "mission": mission,
        "next_action": (
            "Complete the mission and submit the attempt."
        ),
    }


# ---------------------------------------------------------------------------
# ATTEMPT SUBMISSION
# ---------------------------------------------------------------------------

@mcp.tool()
def submit_attempt(
    skill: str,
    mission: str,
    learner_response: str,
    attempt_type: str = "text",
    learner_id: str = "demo-learner",
    practice: bool = False,
) -> dict:

    """
    Submit and record a learner's work for evaluation.
    """
    learner = get_learner(learner_id)
    valid_attempt_types = {
        "code",
        "text",
        "answer",
    }

    normalized_type = attempt_type.strip().lower()

    if normalized_type not in valid_attempt_types:
        return {
            "status": "error",
            "message": (
                "Invalid attempt_type. Choose one of: "
                "code, text, or answer."
            ),
        }

    if not learner_response.strip():
        return {
            "status": "error",
            "message": (
                "learner_response cannot be empty."
            ),
        }

    attempt = {
        "skill": skill,
        "mission": mission,
        "attempt_type": normalized_type,
        "learner_response": learner_response,
        "evaluation": None,
    }

    learner.add_attempt(attempt)

    return {
        "status": "submitted",
        "learner_id": learner.learner_id,
        "skill": skill,
        "mission": mission,
        "attempt_type": normalized_type,
        "learner_response": learner_response,
        "next_action": (
            "Evaluate the learner's attempt."
        ),
    }


# ---------------------------------------------------------------------------
# ATTEMPT EVALUATION
# ---------------------------------------------------------------------------

@mcp.tool()
def evaluate_attempt(
    skill: str,
    mission: str,
    learner_response: str,
    attempt_type: str = "text",
    learner_id: str = "demo-learner",
    practice: bool = False,
) -> dict:
    """
    Evaluate a learner's submitted work using Amazon Bedrock,
    then validate the result using the deterministic Ground Truth layer.

    Bedrock provides evidence and analysis.
    Ground Truth determines the authoritative score and pass/fail state.

    IMPORTANT:
        Learning progression decisions are NOT taken from the AI-generated
        next_action. They are handled deterministically by
        adapt_learning_mission().
    """
    learner = get_learner(learner_id)

    valid_attempt_types = {
        "code",
        "text",
        "answer",
    }

    normalized_type = attempt_type.strip().lower()

    if normalized_type not in valid_attempt_types:
        return {
            "status": "error",
            "message": (
                "Invalid attempt_type. Choose one of: "
                "code, text, or answer."
            ),
        }

    if not learner_response.strip():
        return {
            "status": "error",
            "message": (
                "learner_response cannot be empty."
            ),
        }

    # -----------------------------------------------------------------------
    # Resolve the learner-facing mission into the canonical mission.
    # -----------------------------------------------------------------------

    if practice:
        practice_state = learner.get_active_practice(skill) or {}
        parent_mission_id = practice_state.get("parent_mission_id")
        parent_lookup = get_mission_by_id(parent_mission_id) if parent_mission_id else None

        if parent_lookup is None:
            return {
                "status": "error",
                "message": "Active practice has no valid parent mission.",
            }

        _, parent_mission = parent_lookup
        targeted_criteria = set(practice_state.get("targeted_criteria", []))

        mission_data = {
            **parent_mission,
            "id": parent_mission.get("id"),
            "title": mission,
            "mission": mission,
            "description": practice_state.get("exercise", {}).get("objective") or practice_state.get("exercise", {}).get("instructions") or parent_mission.get("description", ""),
            "criteria": [
                criterion
                for criterion in parent_mission.get("criteria", [])
                if criterion.get("id") in targeted_criteria
            ],
        }
    else:
        mission_data = resolve_mission(
            skill=skill,
            mission=mission,
        )
    mission_data["attempt_type"] = normalized_type


    attempt_data = {
        "learner_id": learner.learner_id,
        "skill": skill,
        "mission": mission,
        "mission_id": mission_data.get("id"),
        "attempt_type": normalized_type,
        "learner_response": learner_response,
    }

    # -----------------------------------------------------------------------
    # AI evaluation + deterministic Ground Truth validation.
    # -----------------------------------------------------------------------

    try:
        final_evaluation = assessment_service.evaluate(
            mission=mission_data,
            attempt=attempt_data,
        )

    except Exception as exc:
        return {
            "status": "error",
            "message": "Assessment failed.",
            "error_type": type(exc).__name__,
        }
    # -----------------------------------------------------------------------
    # Attach evaluation to existing attempt.
    # -----------------------------------------------------------------------

    matching_attempt = None

    for existing_attempt in reversed(
        learner.attempts
    ):
        if (
            existing_attempt.get("skill") == skill
            and existing_attempt.get("mission") == mission
            and existing_attempt.get("attempt_type")
            == normalized_type
            and existing_attempt.get("learner_response")
            == learner_response
            and existing_attempt.get("evaluation") is None
        ):
            matching_attempt = existing_attempt
            break

    if matching_attempt is not None:
        matching_attempt["mission_id"] = attempt_data.get("mission_id")
        matching_attempt["evaluation"] = final_evaluation

    else:
        learner.add_attempt(
            {
                **attempt_data,
                "evaluation": final_evaluation,
            }
        )

    # -----------------------------------------------------------------------
    # Create structured evidence from the authoritative evaluation.
    # -----------------------------------------------------------------------

    evidence = {
        "id": f"evidence-{uuid.uuid4().hex[:12]}",
        "learner_id": learner.learner_id,
        "skill": skill,
        "mission_id": mission_data.get("id"),
        "mission": mission_data.get("mission"),
        "attempt_type": normalized_type,
        "score": final_evaluation.get("score", 0),
        "passed": final_evaluation.get("passed", False),
        "passed_criteria": final_evaluation.get(
            "passed_criteria",
            0,
        ),
        "total_criteria": final_evaluation.get(
            "total_criteria",
            0,
        ),
        "criteria": final_evaluation.get(
            "criteria",
            {},
        ),
        "strengths": final_evaluation.get(
            "strengths",
            [],
        ),
        "weaknesses": final_evaluation.get(
            "weaknesses",
            [],
        ),
        "feedback": final_evaluation.get(
            "feedback",
            "",
        ),
    }

    learner.add_evidence(evidence)

    if matching_attempt is not None:
        matching_attempt["evidence_id"] = evidence["id"]
    else:
        learner.attempts[-1]["evidence_id"] = evidence["id"]

    # -----------------------------------------------------------------------
    # Derive demonstrated capability from successful evidence.
    # -----------------------------------------------------------------------

    if final_evaluation.get("passed") is True and not practice:
        concept = get_concept_for_mission(
            skill=skill,
            mission_id=mission_data.get("id", ""),
        )

        concepts = get_concepts_for_mission(
            skill=skill,
            mission_id=mission_data.get("id", ""),
        )

        concept_ids = [
            item.get("id")
            for item in concepts
            if item.get("id")
        ]

        demonstrated_criteria = [
            criterion
            for criterion in final_evaluation.get(
                "criteria",
                [],
            )
            if isinstance(criterion, dict)
            and criterion.get("passed") is True
        ]

        capability = {
            "id": f"capability-{uuid.uuid4().hex[:12]}",
            "learner_id": learner.learner_id,
            "skill": skill,
            "mission_id": mission_data.get("id"),
            "mission": mission_data.get("mission"),
            "concept_id": (
                concept.get("id")
                if concept
                else None
            ),
            "concept_ids": concept_ids,
            "status": "demonstrated",
            "score": final_evaluation.get("score", 0),
            "passed": True,
            "evidence_ids": [evidence["id"]],
            "demonstrated_criteria": demonstrated_criteria,
        }

        learner.add_capability(capability)

    # -----------------------------------------------------------------------
    # Update learner profile.
    # -----------------------------------------------------------------------

    learner.update_skill_profile(
        strengths=final_evaluation["strengths"],
        weaknesses=final_evaluation["weaknesses"],
    )

    if not practice:
        learner.record_mastery(
            skill=skill,
            mission=mission_data["mission"],
            status=final_evaluation.get(
                "status",
                "needs_practice",
            ),
            score=final_evaluation.get("score", 0),
            passed=final_evaluation.get("passed", False),
            passed_criteria=final_evaluation.get(
                "passed_criteria",
                0,
            ),
            total_criteria=final_evaluation.get(
                "total_criteria",
                0,
            ),
            evidence={
                "criteria": final_evaluation.get(
                    "criteria",
                    {},
                ),
                "strengths": final_evaluation.get(
                    "strengths",
                    [],
                ),
                "weaknesses": final_evaluation.get(
                    "weaknesses",
                    [],
                ),
                "feedback": final_evaluation.get(
                    "feedback",
                    "",
                ),
            },
        )

    # -----------------------------------------------------------------------
    # Return authoritative evaluation.
    #
    # IMPORTANT:
    # Do NOT return final_evaluation["next_action"] here.
    #
    # next_action is a progression decision and is owned by
    # adapt_learning_mission().
    # -----------------------------------------------------------------------

    return {
        "status": "evaluated",
        "learner_id": learner.learner_id,
        "skill": skill,
        "mission": mission,
        "mission_id": mission_data.get("id"),
        "attempt_type": normalized_type,

        # AUTHORITATIVE RESULT
        "score": final_evaluation["score"],
        "passed": final_evaluation["passed"],

        # GROUND TRUTH
        "passed_criteria": (
            final_evaluation["passed_criteria"]
        ),
        "total_criteria": (
            final_evaluation["total_criteria"]
        ),
        "mastery_status": (
            final_evaluation["status"]
        ),

        # AI EVIDENCE
        "criteria": final_evaluation["criteria"],
        "strengths": final_evaluation["strengths"],
        "weaknesses": final_evaluation["weaknesses"],
        "feedback": final_evaluation["feedback"],
        "evidence_id": evidence["id"],
    }



# ---------------------------------------------------------------------------
# BOSS FIGHT LIFECYCLE
# ---------------------------------------------------------------------------

def _boss_skill_key(value: str) -> str:
    return str(value).strip().casefold().replace("_", "-").replace(" ", "-")


def _resolve_boss_parent(skill: str, parent_mission_id: str):
    """Resolve a Boss Fight parent by canonical catalog ID and skill."""
    if not str(skill).strip() or not str(parent_mission_id).strip():
        return None

    resolved = get_mission_by_id(parent_mission_id)
    if resolved is None:
        return None

    canonical_skill, mission = resolved
    if _boss_skill_key(canonical_skill) != _boss_skill_key(skill):
        return None

    return canonical_skill, mission


@mcp.tool()
def create_boss_fight(
    skill: str,
    parent_mission_id: str,
    learner_id: str = "demo-learner",
) -> dict:
    """Create an independent Boss Fight linked to a catalog mission."""
    resolved = _resolve_boss_parent(skill, parent_mission_id)
    if resolved is None:
        return {
            "status": "error",
            "message": "Unknown mission ID or mission does not belong to this skill.",
        }

    canonical_skill, mission = resolved
    learner = get_learner(learner_id)

    try:
        challenge = boss_fight_engine.create_challenge(
            learner=learner,
            skill=canonical_skill,
            parent_mission_id=mission["id"],
            parent_mission_title=mission["title"],
            challenge_brief={
                "instructions": mission.get("description", ""),
                "skills": list(mission.get("skills", [])),
                "criteria": deepcopy(mission.get("criteria", [])),
            },
        )
    except (TypeError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}

    return {"status": "created", "challenge": challenge}


@mcp.tool()
def start_boss_fight(
    challenge_id: str,
    skill: str,
    parent_mission_id: str,
    learner_id: str = "demo-learner",
) -> dict:
    """Start a ready Boss Fight for its owning learner."""
    resolved = _resolve_boss_parent(skill, parent_mission_id)
    if resolved is None:
        return {
            "status": "error",
            "message": "Unknown mission ID or mission does not belong to this skill.",
        }

    canonical_skill, mission = resolved
    learner = get_learner(learner_id)

    try:
        challenge = boss_fight_engine.start_challenge(
            learner,
            challenge_id,
            skill=canonical_skill,
            parent_mission_id=mission["id"],
        )
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    return {"status": "started", "challenge": challenge}


@mcp.tool()
def continue_boss_fight_interview(
    challenge_id: str,
    skill: str,
    parent_mission_id: str,
    learner_response: str = "",
    attempt_type: str = "text",
    learner_id: str = "demo-learner",
) -> dict:
    """Continue an interview without finalizing the assessment."""
    resolved = _resolve_boss_parent(skill, parent_mission_id)
    if resolved is None:
        return {
            "status": "error",
            "message": "Unknown mission ID or mission does not belong to this skill.",
        }

    canonical_skill, parent = resolved
    normalized_type = str(attempt_type).strip().lower()
    if normalized_type not in {"code", "text", "answer"}:
        return {"status": "error", "message": "attempt_type must be code, text, or answer."}
    if not isinstance(learner_response, str):
        return {"status": "error", "message": "learner_response must be text."}

    learner = get_learner(learner_id)
    try:
        challenge = boss_fight_engine.get_challenge(
            learner, challenge_id, skill=canonical_skill,
            parent_mission_id=parent["id"],
        )
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    if challenge["status"] != "in_progress":
        return {
            "status": "error",
            "message": "Only an in-progress Boss Fight can continue its interview.",
        }

    transcript = challenge.get("interview_transcript", [])
    response_text = learner_response.strip()
    if not response_text and transcript:
        return {
            "status": "error",
            "message": "Provide an answer before requesting the next question.",
        }

    prompt_transcript = list(transcript)
    if response_text:
        prompt_transcript.append({
            "role": "learner",
            "content": response_text[:12000],
            "attempt_type": normalized_type,
        })

    mission_data = {
        **parent,
        "id": parent["id"],
        "skill": canonical_skill,
        "title": parent["title"],
        "mission": parent["title"],
    }

    try:
        question = boss_fight_interviewer.generate_question(
            mission=mission_data,
            challenge=challenge,
            transcript=prompt_transcript,
        )
        updated = boss_fight_engine.append_interview_exchange(
            learner, challenge_id, skill=canonical_skill,
            parent_mission_id=parent["id"],
            learner_response=response_text,
            attempt_type=normalized_type,
            examiner_response=question,
        )
    except (TypeError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {
            "status": "error",
            "message": "The AI examiner could not generate the next question.",
            "error_type": type(exc).__name__,
        }

    return {
        "status": "interview_continued",
        "challenge": updated,
        "examiner_message": question,
        "turn_count": len(updated.get("interview_transcript", [])),
    }


@mcp.tool()
def evaluate_boss_fight(
    challenge_id: str,
    skill: str,
    parent_mission_id: str,
    learner_response: str,
    attempt_type: str = "text",
    learner_id: str = "demo-learner",
) -> dict:
    """
    Assess Boss Fight work and record challenge-linked evidence.

    This deliberately does not award capabilities, record parent mission
    mastery, or advance the ordinary learning mission.
    """
    resolved = _resolve_boss_parent(skill, parent_mission_id)
    if resolved is None:
        return {
            "status": "error",
            "message": "Unknown mission ID or mission does not belong to this skill.",
        }

    canonical_skill, parent = resolved
    normalized_type = str(attempt_type).strip().lower()
    if normalized_type not in {"code", "text", "answer"}:
        return {
            "status": "error",
            "message": "attempt_type must be code, text, or answer.",
        }

    if not isinstance(learner_response, str) or not learner_response.strip():
        return {
            "status": "error",
            "message": "A non-empty learner response is required.",
        }

    learner = get_learner(learner_id)

    try:
        challenge = boss_fight_engine.get_challenge(
            learner,
            challenge_id,
            skill=canonical_skill,
            parent_mission_id=parent["id"],
        )
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    if challenge["status"] != "in_progress":
        return {
            "status": "error",
            "message": "Only an in-progress Boss Fight can be evaluated.",
        }

    mission_data = {
        **parent,
        "id": parent["id"],
        "skill": canonical_skill,
        "title": parent["title"],
        "mission": parent["title"],
    }
    attempt_data = {
        "learner_id": learner.learner_id,
        "skill": canonical_skill,
        "mission": parent["title"],
        "mission_id": parent["id"],
        "attempt_type": normalized_type,
        "learner_response": learner_response,
        "boss_fight_id": challenge_id,
        "interview_transcript": deepcopy(
            challenge.get("interview_transcript", [])
        ),
    }

    try:
        raw_evaluation = assessment_service.evaluate(
            mission=mission_data,
            attempt=attempt_data,
        )
    except Exception as exc:
        return {
            "status": "error",
            "message": "Boss Fight assessment failed.",
            "error_type": type(exc).__name__,
        }

    if not isinstance(raw_evaluation, dict):
        return {
            "status": "error",
            "message": "Assessment returned an invalid result.",
        }

    evidence_id = f"evidence-{uuid.uuid4().hex[:12]}"
    evaluation = {
        **raw_evaluation,
        "status": "evaluated",
        "learner_id": learner.learner_id,
        "skill": canonical_skill,
        "mission": parent["title"],
        "mission_id": parent["id"],
        "attempt_type": normalized_type,
        "mastery_status": raw_evaluation.get(
            "mastery_status",
            raw_evaluation.get("status", "needs_practice"),
        ),
        "boss_fight_id": challenge_id,
        "evidence_id": evidence_id,
    }

    # Validate and finalize the challenge before persisting attempt/evidence.
    try:
        completed_challenge = boss_fight_engine.record_evaluation(
            learner,
            challenge_id,
            skill=canonical_skill,
            parent_mission_id=parent["id"],
            evaluation=evaluation,
        )
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    evidence = {
        "id": evidence_id,
        "learner_id": learner.learner_id,
        "skill": canonical_skill,
        "mission_id": parent["id"],
        "mission": parent["title"],
        "attempt_type": normalized_type,
        "evidence_type": "boss_fight",
        "boss_fight_id": challenge_id,
        "score": evaluation["score"],
        "passed": evaluation["passed"],
        "passed_criteria": evaluation["passed_criteria"],
        "total_criteria": evaluation["total_criteria"],
        "criteria": evaluation.get("criteria", {}),
        "strengths": evaluation.get("strengths", []),
        "weaknesses": evaluation.get("weaknesses", []),
        "feedback": evaluation.get("feedback", ""),
    }

    learner.add_attempt({
        **attempt_data,
        "evaluation": evaluation,
        "evidence_id": evidence_id,
    })
    learner.add_evidence(evidence)

    if evaluation.get("passed") is True:
        learner.award_achievement({
            "achievement_id": "boss-fight-first-victory",
            "title": "Boss Fight: First Victory",
            "description": "Passed an independent practical assessment.",
            "icon": "trophy",
            "skill": canonical_skill,
            "boss_fight_id": challenge_id,
            "evidence_id": evidence_id,
        })

    return {
        "status": "evaluated",
        "challenge": completed_challenge,
        "evaluation": evaluation,
        "evidence": evidence,
    }


@mcp.tool()
def get_boss_fight(
    challenge_id: str,
    skill: str,
    parent_mission_id: str,
    learner_id: str = "demo-learner",
) -> dict:
    """Retrieve one Boss Fight owned by the specified learner."""
    resolved = _resolve_boss_parent(skill, parent_mission_id)
    if resolved is None:
        return {
            "status": "error",
            "message": "Unknown mission ID or mission does not belong to this skill.",
        }

    canonical_skill, mission = resolved
    learner = get_learner(learner_id)

    try:
        challenge = boss_fight_engine.get_challenge(
            learner,
            challenge_id,
            skill=canonical_skill,
            parent_mission_id=mission["id"],
        )
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    return {"status": "retrieved", "challenge": challenge}


@mcp.tool()
def get_boss_fights(
    learner_id: str = "demo-learner",
    skill: str | None = None,
) -> dict:
    """List a learner's Boss Fights, optionally filtered by skill."""
    learner = get_learner(learner_id)
    challenges = [
        item
        for item in learner.boss_fights
        if (
            not skill
            or _boss_skill_key(item.get("skill", ""))
            == _boss_skill_key(skill)
        )
    ]

    # Return detached data so callers cannot mutate stored learner state.
    from copy import deepcopy
    return {
        "status": "retrieved",
        "learner_id": learner.learner_id,
        "boss_fights": deepcopy(challenges),
        "count": len(challenges),
    }



# ---------------------------------------------------------------------------
# WEAKNESS IDENTIFICATION
# ---------------------------------------------------------------------------

@mcp.tool()
def identify_weaknesses(
    skill: str,
    evaluation: dict,
) -> dict:
    """
    Identify the learner's skill gaps from an attempt evaluation.
    """

    if evaluation.get("status") != "evaluated":
        return {
            "status": "error",
            "message": (
                "A valid evaluation result is required."
            ),
        }

    weaknesses = evaluation.get(
        "weaknesses",
        [],
    )

    strengths = evaluation.get(
        "strengths",
        [],
    )

    mastery_status = evaluation.get("mastery_status")
    passed = evaluation.get("passed")
    is_mastered = passed is True and mastery_status == "mastered"

    if is_mastered:
        return {
            "status": "identified",
            "skill": skill,
            "weaknesses": [],
            "strengths": strengths,
            "message": (
                "No significant skill gaps were identified. "
                "The learner demonstrated the required skills."
            ),
            "next_action": (
                "Create a more advanced mission."
            ),
        }

    return {
        "status": "identified",
        "skill": skill,
        "weaknesses": weaknesses,
        "strengths": strengths,
        "message": (
            "The learner should focus on the identified skill gaps "
            "before progressing to a more advanced mission."
        ),
        "next_action": (
            "Generate a targeted exercise for the weaknesses."
        ),
    }


# ---------------------------------------------------------------------------
# TARGETED EXERCISE GENERATION
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_targeted_exercise(
    skill: str,
    weaknesses: list[str],
    failed_criteria: list[dict] | None = None,
) -> dict:
    """
    Generate a practical exercise targeting the learner's weaknesses.
    """

    normalized_skill = skill.strip().lower()

    failed_ids = {
        str(criterion.get("id"))
        for criterion in (failed_criteria or [])
        if (
            isinstance(criterion, dict)
            and criterion.get("id")
        )
    }

    # -----------------------------------------------------------------------
    # Python targeted exercise for the guessing-game weakness.
    # -----------------------------------------------------------------------

    if (
        normalized_skill == "python"
        and "multiple_attempts" in failed_ids
    ):
        exercise = {
            "title": (
                "Guessing Game Boss Fight: The Loop"
            ),
            "objective": (
                "Upgrade a one-guess game into a replayable game "
                "that continues until the learner guesses correctly."
            ),
            "instructions": [
                (
                    "Keep the random target number between 1 and 10."
                ),
                (
                    "Use a while loop to accept guesses until "
                    "the answer is correct."
                ),
                (
                    "Tell the learner whether each guess is "
                    "too high or too low."
                ),
                (
                    "Count and display the number of attempts."
                ),
            ],
            "success_signal": (
                "The game accepts more than one guess and stops "
                "only after the correct guess."
            ),
            "targeted_skills": weaknesses,
            "targeted_criteria": sorted(
                failed_ids
            ),
        }

    elif (
        normalized_skill == "python"
        and (
            "track_score" in failed_ids
            or "final_score" in failed_ids
        )
    ):
        exercise = {
            "title": (
                "Quiz Score Tracking Challenge"
            ),
            "objective": (
                "Upgrade the quiz so it tracks correct answers "
                "and displays the learner's final score."
            ),
            "instructions": [
                (
                    "Create a score variable initialized before "
                    "the quiz loop."
                ),
                (
                    "Increase the score when the learner answers "
                    "a question correctly."
                ),
                (
                    "Keep the score available across all quiz "
                    "questions."
                ),
                (
                    "Display the final score after all questions "
                    "have been processed."
                ),
            ],
            "success_signal": (
                "The quiz accumulates the learner's score across "
                "questions and displays the final score."
            ),
            "targeted_skills": weaknesses,
            "targeted_criteria": sorted(
                failed_ids
            ),
        }

    elif (
        normalized_skill == "python"
        and "multiple_questions" in failed_ids
    ):
        exercise = {
            "title": (
                "Quiz Loop Challenge"
            ),
            "objective": (
                "Upgrade the quiz so multiple questions are "
                "processed using a loop."
            ),
            "instructions": [
                (
                    "Store the quiz questions and expected answers "
                    "in a list or another iterable structure."
                ),
                (
                    "Use a loop to process each question "
                    "without repeating the same code manually."
                ),
                (
                    "Check each learner answer and increment "
                    "the score when it is correct."
                ),
                (
                    "Display the final score after the loop completes."
                ),
            ],
            "success_signal": (
                "The quiz processes multiple questions through "
                "a loop and produces the correct final score."
            ),
            "targeted_skills": weaknesses,
            "targeted_criteria": sorted(
                failed_ids
            ),
        }

    elif (
        normalized_skill == "python"
        and "add_expense_function" in failed_ids
    ):
        exercise = {
            "title": (
                "Expense Tracker Add-Expense Challenge"
            ),
            "objective": (
                "Practice defining and using a function that "
                "adds an expense to the expense list."
            ),
            "instructions": [
                (
                    "Create a function named add_expense that "
                    "accepts an expense amount and an expense list."
                ),
                (
                    "Add the expense amount to the list inside "
                    "the function."
                ),
                (
                    "Call the function to add at least one expense."
                ),
                (
                    "Display the updated expense list."
                ),
            ],
            "success_signal": (
                "The add_expense function accepts an expense amount "
                "and list, adds the expense to the list, and is "
                "called successfully."
            ),
            "targeted_skills": weaknesses,
            "targeted_criteria": sorted(
                failed_ids
            ),
        }

    elif (
        normalized_skill == "python"
        and "total_expense_function" in failed_ids
    ):
        exercise = {
            "title": (
                "Expense Tracker Function Challenge"
            ),
            "objective": (
                "Practice defining and using a function that "
                "calculates the total of expense amounts."
            ),
            "instructions": [
                (
                    "Create a function named total_expense that "
                    "accepts a list of expense amounts."
                ),
                (
                    "Use the function to calculate the total "
                    "of all expense amounts."
                ),
                (
                    "Return the calculated total from the function."
                ),
                (
                    "Call the function with a sample expense list "
                    "and display the result."
                ),
            ],
            "success_signal": (
                "The total_expense function accepts expense amounts, "
                "calculates their total, returns the result, and "
                "is called successfully."
            ),
            "targeted_skills": weaknesses,
            "targeted_criteria": sorted(
                failed_ids
            ),
        }

    elif normalized_skill == "python":
        exercise = {
            "title": (
                "Build a Guessing Game Core"
            ),
            "objective": (
                "Practice random number generation, learner input, "
                "comparison, and conditional logic."
            ),
            "objective": (
                "Practice random number generation, learner input, "
                "comparison, and conditional logic."
            ),
            "instructions": [
                (
                    "Generate a random number between 1 and 10."
                ),
                (
                    "Ask the user to guess the number."
                ),
                (
                    "Compare the guess with the generated number."
                ),
                (
                    "Tell the user whether the guess is correct."
                ),
            ],
            "targeted_skills": weaknesses,
            "targeted_criteria": sorted(
                failed_ids
            ),
        }

    else:
        exercise = {
            "title": (
                f"Practice {skill.title()} Fundamentals"
            ),
            "objective": (
                f"Complete a practical exercise focused on "
                f"your identified {skill.title()} skill gaps."
            ),
            "instructions": [
                f"Practice: {weakness}"
                for weakness in weaknesses
            ],
            "targeted_skills": weaknesses,
            "targeted_criteria": sorted(
                failed_ids
            ),
        }

    return {
        "status": "created",
        "skill": skill,
        "exercise": exercise,
        "next_action": (
            "Complete the targeted exercise and submit the attempt."
        ),
    }


# ---------------------------------------------------------------------------
# MISSION PROGRESSION
# ---------------------------------------------------------------------------

def get_next_mission(
    skill: str,
    current_mission: str,
) -> dict | None:
    """
    Return the next mission in the learner's progression path.

    The ordered mission definitions come from the course catalog.
    The function is deterministic so the learner cannot accidentally
    skip or receive an invented mission.
    """

    normalized_skill = skill.strip().lower()
    normalized_mission = current_mission.strip().lower()

    missions = get_missions(
        normalized_skill,
    )

    for index, mission in enumerate(missions):
        mission_id = mission["id"].strip().lower()
        mission_title = mission["title"].strip().lower()

        if (
            mission_id == normalized_mission
            or mission_title == normalized_mission
            or normalized_mission.startswith(mission_title)
        ):
            next_index = index + 1

            if next_index < len(missions):
                next_mission = missions[next_index]

                return {
                    "id": next_mission["id"],
                    "skill": skill,
                    "title": next_mission["title"],
                    "description": next_mission["description"],
                    "skills": next_mission["skills"],
                }

            return None

    return None


# ---------------------------------------------------------------------------
# ADAPTIVE LEARNING
# ---------------------------------------------------------------------------

@mcp.tool()
def adapt_learning_mission(
    skill: str,
    evaluation: dict,
    learner_id: str = "demo-learner",
    practice: bool = False,
) -> dict:
    """
    Adapt the learner's next action based on an attempt evaluation.

    Progression decisions are deterministic and do not depend
    on Bedrock's generated next_action.
    """
    learner = get_learner(learner_id)

    if evaluation.get("status") != "evaluated":
        return {
            "status": "error",
            "message": (
                "A valid evaluation result is required."
            ),
        }

    weaknesses = evaluation.get(
        "weaknesses",
        [],
    )

    failed_criteria = [
        criterion
        for criterion in evaluation.get(
            "criteria",
            [],
        )
        if (
            isinstance(criterion, dict)
            and criterion.get("passed") is False
        )
    ]

    strengths = evaluation.get(
        "strengths",
        [],
    )

    score = evaluation.get(
        "score",
        0,
    )

    passed = evaluation.get(
        "passed",
        False,
    )

    # Keep the learner profile synchronized.
    learner.update_skill_profile(
        strengths=strengths,
        weaknesses=weaknesses,
    )

    capability_profile = learner.get_capability_profile()

    # -----------------------------------------------------------------------
    # Mastery path.
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Targeted practice path.
    # -----------------------------------------------------------------------

    if practice:
        active_mission = learner.get_active_mission(skill)

        if passed is True:
            learner.clear_active_practice(skill)

            return {
                "status": "adapted",
                "learner_id": learner.learner_id,
                "skill": skill,
                "score": score,
                "passed": passed,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "capability_profile": capability_profile,
                "active_mission": active_mission,
                "targeted_exercise": None,
                "mission_completed": False,
                "practice_completed": True,
                "next_action": "retry_parent_mission",
                "message": (
                    "The targeted practice was completed successfully. "
                    "The parent mission remains active and can now be retried."
                ),
            }

        targeted_exercise = generate_targeted_exercise(
            skill=skill,
            weaknesses=weaknesses,
            failed_criteria=failed_criteria,
        )

        parent_mission_id = evaluation.get("mission_id")

        if active_mission and active_mission.get("mission_id"):
            parent_mission_id = active_mission.get("mission_id")

        learner.set_active_practice(
            {
                "skill": skill,
                "parent_mission_id": parent_mission_id,
                "parent_mission": (
                    active_mission.get("title")
                    if active_mission
                    else evaluation.get("mission")
                ),
                "exercise": targeted_exercise.get("exercise"),
                "targeted_criteria": [
                    criterion.get("id")
                    for criterion in failed_criteria
                    if isinstance(criterion, dict)
                    and criterion.get("id")
                ],
                "targeted_skills": weaknesses,
                "status": "ready",
            }
        )

        return {
            "status": "adapted",
            "learner_id": learner.learner_id,
            "skill": skill,
            "score": score,
            "passed": passed,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "capability_profile": capability_profile,
            "active_mission": active_mission,
            "targeted_exercise": targeted_exercise,
            "mission_completed": False,
            "practice_completed": False,
            "next_action": (
                "Complete the targeted exercise, submit the attempt, "
                "and evaluate the new attempt."
            ),
        }

    # -----------------------------------------------------------------------
    # Mastery path.
    # -----------------------------------------------------------------------

    mastery_status = evaluation.get("mastery_status")
    is_mastered = (
        passed is True
        and mastery_status == "mastered"
    )

    if is_mastered:
        active_mission = learner.get_active_mission(skill)

        # Resolve the mission that was actually evaluated.
        current_mission_id = evaluation.get(
            "mission_id",
            "",
        )

        current_mission_title = evaluation.get(
            "mission",
            "",
        )

        if active_mission:
            active_mission_id = active_mission.get(
                "mission_id",
                "",
            )

            if active_mission_id:
                current_mission_id = active_mission_id

            current_mission_title = active_mission.get(
                "title",
                current_mission_title,
            )

        # ---------------------------------------------------------------
        # Record the completed mission exactly once.
        # ---------------------------------------------------------------

        already_completed = any(
            completed.get("mission_id")
            == current_mission_id
            for completed in learner.completed_missions
            if isinstance(completed, dict)
        )

        if not already_completed:
            learner.add_completed_mission(
                {
                    "mission_id": current_mission_id,
                    "title": current_mission_title,
                    "skill": skill,
                    "score": score,
                    "status": "completed",
                }
            )

        learner.award_achievement({
            "achievement_id": "first-mission-mastered",
            "title": "First Mission Mastered",
            "description": "Mastered a mission in this learning path.",
            "icon": "trophy",
            "skill": skill,
        })

        # ---------------------------------------------------------------
        # Clear the active mission now that it has been mastered.
        # ---------------------------------------------------------------

        learner.clear_active_mission(skill)

        # ---------------------------------------------------------------
        # Find the next mission.
        # ---------------------------------------------------------------

        next_mission = get_next_mission(
            skill=skill,
            current_mission=current_mission_id,
        )

        # ---------------------------------------------------------------
        # Learning path complete.
        # ---------------------------------------------------------------

        if next_mission is None:
            return {
                "status": "adapted",
                "learner_id": learner.learner_id,
                "skill": skill,
                "score": score,
                "passed": passed,
                "strengths": strengths,
                "weaknesses": [],
                "capability_profile": capability_profile,
                "next_action": "learning_path_complete",
                "next_mission": None,
                "active_mission": None,
                "mission_completed": True,
                "message": (
                    "The learner has mastered the available missions "
                    "for this learning path."
                ),
            }

        # The next mission is available but remains inactive.
        # The learner must explicitly choose to start it.
        return {
            "status": "adapted",
            "learner_id": learner.learner_id,
            "skill": skill,
            "score": score,
            "passed": passed,
            "strengths": strengths,
            "weaknesses": [],
            "capability_profile": capability_profile,
            "next_action": "create_advanced_mission",
            "next_mission": next_mission,
            "active_mission": None,
            "mission_completed": True,
            "message": (
                "The learner demonstrated mastery. "
                "The completed mission has been recorded and "
                "the next mission is available to start."
            ),
        }

    # -----------------------------------------------------------------------
    # Remediation path.
    # -----------------------------------------------------------------------

    # The learner remains on the current mission until mastery is achieved.
    active_mission = learner.get_active_mission(skill)

    targeted_exercise = generate_targeted_exercise(
        skill=skill,
        weaknesses=weaknesses,
        failed_criteria=failed_criteria,
    )

    parent_mission_id = evaluation.get("mission_id")

    if active_mission and active_mission.get("mission_id"):
        parent_mission_id = active_mission.get("mission_id")

    learner.set_active_practice(
        {
            "skill": skill,
            "parent_mission_id": parent_mission_id,
            "parent_mission": (
                active_mission.get("title")
                if active_mission
                else evaluation.get("mission")
            ),
            "exercise": targeted_exercise.get("exercise"),
            "targeted_criteria": [
                criterion.get("id")
                for criterion in failed_criteria
                if isinstance(criterion, dict)
                and criterion.get("id")
            ],
            "targeted_skills": weaknesses,
            "status": "ready",
        }
    )

    return {
        "status": "adapted",
        "learner_id": learner.learner_id,
        "skill": skill,
        "score": score,
        "passed": passed,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "capability_profile": capability_profile,
        "active_mission": active_mission,
        "targeted_exercise": targeted_exercise,
        "mission_completed": False,
        "practice_completed": False,
        "next_action": (
            "Complete the targeted exercise, submit the attempt, "
            "and evaluate the new attempt."
        ),
    }


# ---------------------------------------------------------------------------
# LEARNER STATE
# ---------------------------------------------------------------------------

@mcp.tool()
def get_learner_state(
    learner_id: str = "demo-learner",
    practice: bool = False,
) -> dict:
    """Return the complete state for one learner."""

    learner = get_learner(learner_id)

    return {
        "status": "success",
        "learner": learner.to_dict(),
    }


@mcp.tool()
def get_capability_profile(
    learner_id: str = "demo-learner",
    practice: bool = False,
) -> dict:
    """Return the learner's demonstrated capabilities aggregated by skill."""

    learner = get_learner(learner_id)

    return {
        "status": "success",
        "learner_id": learner.learner_id,
        "capabilities": learner.get_capability_profile(),
    }


def _recommend_next_mission(
    learner: LearnerState,
    skill: str,
) -> dict | None:
    """Recommend an existing mission using the learner's mastery records."""

    missions = get_missions(skill)
    skill_key = skill.strip().lower()

    mastery_records = {}
    for stored_skill, records in learner.mastery.items():
        if stored_skill.strip().lower() == skill_key:
            mastery_records = records
            break

    def normalize(value: str) -> str:
        return "".join(
            character.lower()
            for character in value
            if character.isalnum()
        )

    def mastery_for(mission: dict) -> dict | None:
        accepted_names = {
            normalize(str(mission.get("id", ""))),
            normalize(str(mission.get("title", ""))),
        }

        for recorded_name, result in mastery_records.items():
            if normalize(str(recorded_name)) in accepted_names:
                return result

        return None

    # Address an existing learning gap before moving to new work.
    for mission in missions:
        record = mastery_for(mission)
        if record and record.get("status") == "needs_practice":
            return {
                "id": mission["id"],
                "skill": skill,
                "title": mission["title"],
                "description": mission["description"],
                "skills": mission["skills"],
                "reason": "needs_practice",
            }

    # Otherwise, choose the first mission not yet mastered.
    for mission in missions:
        record = mastery_for(mission)

        if not (
            record
            and record.get("status") == "mastered"
            and record.get("passed") is True
        ):
            return {
                "id": mission["id"],
                "skill": skill,
                "title": mission["title"],
                "description": mission["description"],
                "skills": mission["skills"],
                "reason": "new_mission",
            }

    # No eligible missions remain in this catalog.
    return None

@mcp.tool()
def get_learner_profile(
    learner_id: str = "demo-learner",
    skill: str | None = None,
    learner_level: str | None = None,
    practice: bool = False,
) -> dict:
    """Return the learner's complete or skill-scoped profile."""

    learner = get_learner(learner_id)

    return {
        "status": "success",
        "learner_id": learner.learner_id,
        "profile": learner.get_learner_profile(
            skill=skill,
            learner_level=learner_level,
        ),
    }


# ---------------------------------------------------------------------------
# SERVER ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )
