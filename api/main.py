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


app = FastAPI(
    title="Master It By Doing API",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
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

    The learner provides the skill and current level.
    The learning orchestrator then creates the goal and
    practical mission through the MCP learning engine.
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


class AttemptRequest(BaseModel):
    """
    Request body for submitting a learner attempt.

    The mission is supplied by the frontend so the evaluation
    is performed against the actual mission the learner is viewing.
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
        default="Build an authenticated API",
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

    # -----------------------------------------------------------------------
    # Create orchestrator
    # -----------------------------------------------------------------------

    orchestrator = LearningOrchestrator(
        learner_id=request.learner_id,
        skill=request.skill,
        level=request.level,
    )

    # -----------------------------------------------------------------------
    # Execute GOAL → MISSION
    # -----------------------------------------------------------------------

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
        # Temporary diagnostic output.
        # This will help us identify the real exception behind
        # the ExceptionGroup returned by the MCP client.
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Learning journey could not be started."
                ),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            },
        ) from exc

    # -----------------------------------------------------------------------
    # Return real learning state
    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------
    # Validate attempt
    # -----------------------------------------------------------------------

    if not request.attempt.strip():
        raise HTTPException(
            status_code=400,
            detail="Attempt cannot be empty.",
        )

    # -----------------------------------------------------------------------
    # Validate mission
    # -----------------------------------------------------------------------

    if not request.mission.strip():
        raise HTTPException(
            status_code=400,
            detail="Mission cannot be empty.",
        )

    # -----------------------------------------------------------------------
    # Create orchestrator
    # -----------------------------------------------------------------------

    orchestrator = LearningOrchestrator(
        learner_id=request.learner_id,
        skill=request.skill,
        level=request.level,
        mission=request.mission,
    )

    # -----------------------------------------------------------------------
    # Execute complete learning cycle
    # -----------------------------------------------------------------------

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
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Learning cycle failed.",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        ) from exc

    # -----------------------------------------------------------------------
    # Return complete learning state
    # -----------------------------------------------------------------------

    return {
        "status": "completed",
        "mission_id": mission_id,
        "result": result,
    }