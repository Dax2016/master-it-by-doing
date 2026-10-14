"""
Master It By Doing
Web API

HTTP boundary between the React web application
and the existing learning orchestrator.
"""

from typing import Literal
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.orchestrator import LearningOrchestrator
from content.course_catalog import get_courses, get_mission_by_id


app = FastAPI(
    title="Master It By Doing API",
    version="1.1.0",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------------------------

class StartLearningRequest(BaseModel):
    """
    Request body for starting a learner's journey.
    """

    learner_id: str = Field(
        default="demo-learner",
        min_length=1,
    )

    skill: str = Field(
        default="python",
        min_length=1,
    )

    level: str = Field(
        default="beginner",
        min_length=1,
    )

    mission: str | None = None
    mission_id: str | None = None


class ActivateMissionRequest(BaseModel):
    learner_id: str = Field(default="demo-learner", min_length=1)
    skill: str = Field(default="python", min_length=1)
    level: str = Field(default="beginner", min_length=1)


class AttemptRequest(BaseModel):
    """
    Request body for submitting a learner attempt.
    """

    learner_id: str = Field(
        default="demo-learner",
        min_length=1,
    )

    skill: str = Field(
        default="python",
        min_length=1,
    )

    level: str = Field(
        default="beginner",
        min_length=1,
    )

    mission: str = Field(
        min_length=1,
    )

    attempt: str = Field(
        min_length=1,
    )

    attempt_type: Literal[
        "code",
        "text",
        "answer",
    ] = "code"


# ---------------------------------------------------------------------------
# HEALTH
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict:
    """
    Confirm that the Web API is running.
    """

    return {
        "status": "ok",
        "service": "master-it-by-doing-api",
        "version": app.version,
    }


# ---------------------------------------------------------------------------
# LEARNER STATE
# ---------------------------------------------------------------------------

@app.get("/api/learning/state")
async def get_learning_state(
    learner_id: str = "demo-learner",
    skill: str = "python",
    level: str = "beginner",
) -> dict:
    """
    Return the learner's current persistent learning-engine state.

    This endpoint intentionally does not start a new learning cycle.

    The React application can therefore safely load the dashboard
    without creating a new goal or mission on every page visit.

    Flow:

        React
          ?
        FastAPI
          ?
        LearningOrchestrator
          ?
        MCP
          ?
        LearnerState
    """

    orchestrator = LearningOrchestrator(
        learner_id=learner_id,
        skill=skill,
        level=level,
    )

    try:
        state = await orchestrator.get_learner_state()
        capabilities = await orchestrator.get_capability_profile()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(exc),
                "error_type": type(exc).__name__,
            },
        ) from exc

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Learner state could not be retrieved.",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        ) from exc

    return {
        "status": "ok",
        "learner_id": learner_id,
        "skill": skill,
        "level": level,
        "state": state,
        "capabilities": capabilities,
    }


# ---------------------------------------------------------------------------
# LEARNER CAPABILITIES
# ---------------------------------------------------------------------------

@app.get("/api/learning/capabilities")
async def get_learning_capabilities(
    learner_id: str = "demo-learner",
    skill: str = "python",
    level: str = "beginner",
) -> dict:
    """
    Return the learner's demonstrated capability profile.

    Capabilities are evidence-based. They are derived from
    evaluated learner work rather than self-reported progress.
    """

    orchestrator = LearningOrchestrator(
        learner_id=learner_id,
        skill=skill,
        level=level,
    )

    try:
        capabilities = await orchestrator.get_capability_profile()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(exc),
                "error_type": type(exc).__name__,
            },
        ) from exc

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Capability profile could not be retrieved.",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        ) from exc

    return {
        "status": "ok",
        "learner_id": learner_id,
        "skill": skill,
        "level": level,
        "capabilities": capabilities,
    }


# ---------------------------------------------------------------------------
# MISSION LOOKUP
# ---------------------------------------------------------------------------

@app.get("/api/learning/paths")
async def get_learning_paths() -> dict:
    """Return the available learning paths from the course catalog."""
    return {
        "status": "ok",
        "paths": get_courses(),
    }

@app.post("/api/missions/{mission_id}/activate")
async def activate_mission(
    mission_id: str,
    request: ActivateMissionRequest,
) -> dict:
    """Activate a selected catalog mission for the specified learner."""

    lookup = get_mission_by_id(mission_id.strip())
    if lookup is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown mission ID: {mission_id}",
        )

    canonical_skill, _ = lookup

    def normalize(value: str) -> str:
        return value.strip().casefold().replace("_", "-").replace(" ", "-")

    if normalize(request.skill) != normalize(canonical_skill):
        raise HTTPException(
            status_code=400,
            detail="The mission does not belong to the requested skill.",
        )

    try:
        orchestrator = LearningOrchestrator(
            learner_id=request.learner_id,
            skill=canonical_skill,
            level=request.level,
        )
        result = await orchestrator.activate_mission(mission_id.strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Mission activation failed.",
        ) from exc

    status = result.get("status") if isinstance(result, dict) else None
    if status == "not_found":
        raise HTTPException(status_code=404, detail=result.get("message"))
    if status == "skill_mismatch":
        raise HTTPException(status_code=400, detail=result.get("message"))
    if status == "conflict":
        raise HTTPException(status_code=409, detail=result.get("message"))

    return result


@app.get("/api/missions/{mission_id}")
async def get_mission(
    mission_id: str,
) -> dict:
    """
    Return a canonical mission from the course catalog.

    This endpoint is read-only.

    The frontend should use this endpoint when opening a mission
    rather than starting a new learning cycle just to display it.
    """

    normalized_mission_id = mission_id.strip()

    if not normalized_mission_id:
        raise HTTPException(
            status_code=400,
            detail="Mission ID cannot be empty.",
        )

    mission_lookup = get_mission_by_id(
        normalized_mission_id,
    )

    if mission_lookup is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Unknown mission ID: {normalized_mission_id}",
                "mission_id": normalized_mission_id,
            },
        )

    skill, mission = mission_lookup

    return {
        "status": "ok",
        "mission_id": normalized_mission_id,
        "skill": skill,
        "mission": mission.get(
            "title",
            normalized_mission_id,
        ),
        "title": mission.get(
            "title",
            normalized_mission_id,
        ),
        "description": mission.get(
            "description",
            "",
        ),
        "skills": mission.get(
            "skills",
            [],
        ),
        "criteria": mission.get(
            "criteria",
            [],
        ),
        "concept_id": mission.get(
            "concept_id",
        ),
    }


# ---------------------------------------------------------------------------
# START LEARNING JOURNEY
# ---------------------------------------------------------------------------

@app.post("/api/learning/start")
async def start_learning(
    request: StartLearningRequest,
) -> dict:
    """
    Start a learner's practical learning journey.

    Workflow:

        React
          ?
        FastAPI
          ?
        LearningOrchestrator
          ?
        MCP
          ?
        create_learning_goal
          ?
        create_mission
          ?
        GOAL ? MISSION
    """

    orchestrator = LearningOrchestrator(
        learner_id=request.learner_id,
        skill=request.skill,
        level=request.level,
        mission=request.mission,
        mission_id=request.mission_id,
    )

    try:
        result = await orchestrator.run_learning_cycle()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(exc),
                "error_type": type(exc).__name__,
            },
        ) from exc

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Learning journey could not be started.",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        ) from exc

    return {
        "status": "started",
        "result": result,
    }


# ---------------------------------------------------------------------------
# SUBMIT + EVALUATE
# ---------------------------------------------------------------------------

@app.post("/api/missions/{mission_id}/attempt")
async def submit_mission_attempt(
    mission_id: str,
    request: AttemptRequest,
) -> dict:
    """
    Execute the complete learning cycle for a submitted attempt.

    Workflow:

        React
          ?
        FastAPI
          ?
        LearningOrchestrator
          ?
        MCP
          ?
        submit_attempt
          ?
        evaluate_attempt
          ?
        identify_weaknesses
          ?
        generate_targeted_exercise
          ?
        adapt_learning_mission
          ?
        Real learning state
    """

    if not request.attempt.strip():
        raise HTTPException(
            status_code=400,
            detail="Attempt cannot be empty.",
        )

    if not request.mission.strip():
        raise HTTPException(
            status_code=400,
            detail="Mission cannot be empty.",
        )

    orchestrator = LearningOrchestrator(
        learner_id=request.learner_id,
        skill=request.skill,
        level=request.level,
        mission=request.mission,
        mission_id=mission_id,
    )

    try:
        result = await orchestrator.run_learning_cycle(
            attempt=request.attempt,
            attempt_type=request.attempt_type,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(exc),
                "error_type": type(exc).__name__,
            },
        ) from exc

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Learning cycle failed.",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        ) from exc

    return {
        "status": "completed",
        "mission_id": mission_id,
        "result": result,
    }

# ---------------------------------------------------------------------------
# LEARNER PROFILE
# ---------------------------------------------------------------------------

@app.get("/api/learning/profile")
async def get_learning_profile(
    learner_id: str = "demo-learner",
    skill: str = "python",
    level: str = "beginner",
    all_skills: bool = False,
) -> dict:
    """
    Return the learner's complete capability and learning profile.

    The profile is a read-only projection of existing learner state.
    It does not create or modify goals, missions, attempts, or mastery.
    """

    orchestrator = LearningOrchestrator(
        learner_id=learner_id,
        skill=skill,
        level=level,
    )

    try:
        profile_result = await orchestrator.get_learner_profile(
            include_all_skills=all_skills,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(exc),
                "error_type": type(exc).__name__,
            },
        ) from exc

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Learner profile could not be retrieved.",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        ) from exc

    return {
        "status": "ok",
        "learner_id": learner_id,
        "skill": skill,
        "level": level,
        "profile": profile_result.get("profile", profile_result),


    }

# ---------------------------------------------------------------------------
# BOSS FIGHT API
# ---------------------------------------------------------------------------

class BossFightRequest(BaseModel):
    learner_id: str = Field(default="demo-learner", min_length=1)
    skill: str = Field(default="python", min_length=1)
    parent_mission_id: str = Field(min_length=1)


class BossFightEvaluationRequest(BossFightRequest):
    learner_response: str = Field(min_length=1)
    attempt_type: Literal["code", "text", "answer"] = "text"


async def _call_boss_fight_tool(
    tool_name: str,
    arguments: dict,
) -> dict:
    """Call a Boss Fight MCP tool and translate its result to HTTP semantics."""
    orchestrator = LearningOrchestrator(
        learner_id=arguments.get("learner_id", "demo-learner"),
        skill=arguments.get("skill", "python"),
        level="beginner",
    )

    try:
        raw_result = await orchestrator.mcp.call_tool(
            tool_name,
            arguments,
        )
        result = LearningOrchestrator._extract_result(raw_result)

    except HTTPException:
        raise
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail={
                "message": "The Boss Fight service could not complete the request.",
                "error_type": type(exc).__name__,
            },
        ) from exc

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail="The Boss Fight service returned an invalid response.",
        )

    if result.get("status") == "error":
        message = str(result.get("message", "Boss Fight request failed."))
        lowered = message.lower()

        if any(term in lowered for term in (
            "not found", "unknown", "does not exist", "no such",
        )):
            status_code = 404
        elif any(term in lowered for term in (
            "already started", "already completed", "must be in_progress",
            "must be ready", "invalid state", "cannot be",
        )):
            status_code = 409
        else:
            status_code = 400

        raise HTTPException(
            status_code=status_code,
            detail={"message": message},
        )

    return result


@app.post("/api/boss-fights")
async def create_boss_fight_api(request: BossFightRequest) -> dict:
    """Create a challenge linked to an existing catalog mission."""
    return await _call_boss_fight_tool(
        "create_boss_fight",
        request.model_dump(),
    )


@app.post("/api/boss-fights/{challenge_id}/start")
async def start_boss_fight_api(
    challenge_id: str,
    request: BossFightRequest,
) -> dict:
    """Start a ready challenge owned by the requesting learner."""
    return await _call_boss_fight_tool(
        "start_boss_fight",
        {
            **request.model_dump(),
            "challenge_id": challenge_id,
        },
    )


@app.post("/api/boss-fights/{challenge_id}/evaluate")
async def evaluate_boss_fight_api(
    challenge_id: str,
    request: BossFightEvaluationRequest,
) -> dict:
    """Evaluate a response for an in-progress challenge."""
    return await _call_boss_fight_tool(
        "evaluate_boss_fight",
        {
            **request.model_dump(),
            "challenge_id": challenge_id,
        },
    )


@app.get("/api/boss-fights/{challenge_id}")
async def get_boss_fight_api(
    challenge_id: str,
    learner_id: str = "demo-learner",
    skill: str = "python",
    parent_mission_id: str = "",
) -> dict:
    """Retrieve a specific challenge with its parent mission context."""
    if not parent_mission_id.strip():
        raise HTTPException(
            status_code=422,
            detail="parent_mission_id is required.",
        )

    return await _call_boss_fight_tool(
        "get_boss_fight",
        {
            "challenge_id": challenge_id,
            "learner_id": learner_id,
            "skill": skill,
            "parent_mission_id": parent_mission_id,
        },
    )


@app.get("/api/boss-fights")
async def list_boss_fights_api(
    learner_id: str = "demo-learner",
    skill: str | None = None,
) -> dict:
    """List challenges belonging to one learner, optionally by skill."""
    arguments = {"learner_id": learner_id}
    if skill is not None:
        arguments["skill"] = skill

    return await _call_boss_fight_tool(
        "get_boss_fights",
        arguments,
    )
