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
from content.course_catalog import get_mission_by_id


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
          ↓
        FastAPI
          ↓
        LearningOrchestrator
          ↓
        MCP
          ↓
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
          ↓
        FastAPI
          ↓
        LearningOrchestrator
          ↓
        MCP
          ↓
        create_learning_goal
          ↓
        create_mission
          ↓
        GOAL → MISSION
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
          ↓
        FastAPI
          ↓
        LearningOrchestrator
          ↓
        MCP
          ↓
        submit_attempt
          ↓
        evaluate_attempt
          ↓
        identify_weaknesses
          ↓
        generate_targeted_exercise
          ↓
        adapt_learning_mission
          ↓
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
