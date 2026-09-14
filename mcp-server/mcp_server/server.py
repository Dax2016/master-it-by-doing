from services.assessment.assessment_service import AssessmentService
from mcp.server.fastmcp import FastMCP

from services.learner.learner_state import LearnerState


mcp = FastMCP("Master It By Doing")

learner = LearnerState(learner_id="demo-learner")

# AI evidence collection plus deterministic mission validation.
assessment_service = AssessmentService()


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

    The learner/orchestrator may provide either:

        "Build a Number Guessing Game"

    or:

        "Build a Number Guessing Game: Create a Python program..."

    Ground Truth must receive the canonical mission definition,
    including its authoritative skills.
    """

    missions = {
        "python": {
            "title": "Build a Number Guessing Game",
            "description": (
                "Create a Python program that generates a random number "
                "and lets the learner guess it."
            ),
            "skills": [
                "Variables",
                "Input and output",
                "Conditionals",
                "Loops",
                "Functions",
            ],
        },
        "javascript": {
            "title": "Build a Console To-Do List",
            "description": (
                "Create a JavaScript program that allows a user to add, "
                "view, and remove tasks."
            ),
            "skills": [
                "Variables",
                "Arrays",
                "Functions",
                "Conditionals",
                "Loops",
            ],
        },
    }

    normalized_skill = skill.strip().lower()
    normalized_mission = mission.strip().lower()

    canonical = missions.get(normalized_skill)

    if canonical:
        canonical_title = canonical["title"].strip().lower()

        if (
            normalized_mission == canonical_title
            or normalized_mission.startswith(
                canonical_title + ":"
            )
            or canonical_title in normalized_mission
        ):
            return {
                "skill": skill,
                "title": canonical["title"],
                "mission": canonical["title"],
                "description": canonical["description"],
                "skills": canonical["skills"],
            }

    # Fallback for unknown missions.
    #
    # We intentionally preserve the supplied mission rather than
    # inventing requirements. Ground Truth will therefore only use
    # requirements explicitly available for that mission.
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
) -> dict:
    """
    Create and record a practical learning goal for the learner.

    Args:
        skill: The skill the learner wants to learn.
        learner_level: The learner's current level.
    """

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
        "message": (
            f"Learning goal created: learn {skill} "
            f"at {learner_level} level."
        ),
        "next_action": "Create a practical learning mission.",
    }


# ---------------------------------------------------------------------------
# MISSION CREATION
# ---------------------------------------------------------------------------

@mcp.tool()
def create_mission(
    skill: str,
    learner_level: str = "beginner",
) -> dict:
    """
    Create a practical hands-on learning mission.

    Args:
        skill: The skill the learner wants to practice.
        learner_level: The learner's current level.
    """

    missions = {
        "python": {
            "title": "Build a Number Guessing Game",
            "description": (
                "Create a Python program that generates a random number "
                "and lets the learner guess it."
            ),
            "skills": [
                "Variables",
                "Input and output",
                "Conditionals",
                "Loops",
                "Functions",
            ],
        },
        "javascript": {
            "title": "Build a Console To-Do List",
            "description": (
                "Create a JavaScript program that allows a user to add, "
                "view, and remove tasks."
            ),
            "skills": [
                "Variables",
                "Arrays",
                "Functions",
                "Conditionals",
                "Loops",
            ],
        },
    }

    mission = missions.get(
        skill.strip().lower(),
        {
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
        },
    )

    return {
        "status": "created",
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
) -> dict:
    """
    Submit and record a learner's work for evaluation.

    Args:
        skill: The skill being practiced.
        mission: The mission the learner was assigned.
        learner_response: The learner's actual work or answer.
        attempt_type: The type of submission: code, text, or answer.
    """

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
) -> dict:
    """
    Evaluate a learner's submitted work using Amazon Bedrock,
    then validate the result using the deterministic Ground Truth layer.

    Bedrock provides evidence and analysis.
    Ground Truth determines the authoritative score and pass/fail state.
    """

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
    #
    # This is critical because the orchestrator may pass:
    #
    #   Build a Number Guessing Game:
    #   Create a Python program...
    #
    # while Ground Truth requires:
    #
    #   Build a Number Guessing Game
    #
    # The canonical mission also supplies the authoritative skills.
    # -----------------------------------------------------------------------

    mission_data = resolve_mission(
        skill=skill,
        mission=mission,
    )

    mission_data["attempt_type"] = normalized_type

    attempt_data = {
        "learner_id": learner.learner_id,
        "skill": skill,
        "mission": mission,
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
        matching_attempt["evaluation"] = final_evaluation

    else:
        learner.add_attempt(
            {
                **attempt_data,
                "evaluation": final_evaluation,
            }
        )

    # -----------------------------------------------------------------------
    # Update learner profile.
    # -----------------------------------------------------------------------

    learner.update_skill_profile(
        strengths=final_evaluation["strengths"],
        weaknesses=final_evaluation["weaknesses"],
    )

    # -----------------------------------------------------------------------
    # Return authoritative evaluation.
    # -----------------------------------------------------------------------

    return {
        "status": "evaluated",
        "learner_id": learner.learner_id,
        "skill": skill,
        "mission": mission,
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
        "next_action": final_evaluation["next_action"],
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

    Args:
        skill: The skill being practiced.
        evaluation: The evaluation result returned by evaluate_attempt().
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

    if not weaknesses:
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

    Args:
        skill: The skill being practiced.
        weaknesses: The learner's identified skill gaps.
        failed_criteria: Authoritative criteria that the learner failed.
    """

    if not weaknesses:
        return {
            "status": "error",
            "message": (
                "At least one weakness is required."
            ),
        }

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

    elif normalized_skill == "python":
        exercise = {
            "title": (
                "Build a Guessing Game Core"
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
# ADAPTIVE LEARNING
# ---------------------------------------------------------------------------

@mcp.tool()
def adapt_learning_mission(
    skill: str,
    evaluation: dict,
) -> dict:
    """
    Adapt the learner's next action based on an attempt evaluation.

    Args:
        skill: The skill being practiced.
        evaluation: The evaluation result returned by evaluate_attempt().
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

    # -----------------------------------------------------------------------
    # Mastery path.
    # -----------------------------------------------------------------------

    if not weaknesses:
        return {
            "status": "adapted",
            "learner_id": learner.learner_id,
            "skill": skill,
            "score": score,
            "passed": passed,
            "strengths": strengths,
            "weaknesses": [],
            "next_action": (
                "Create a more advanced mission."
            ),
            "message": (
                "The learner demonstrated the required skills. "
                "Increase the difficulty of the next mission."
            ),
        }

    # -----------------------------------------------------------------------
    # Remediation path.
    # -----------------------------------------------------------------------

    targeted_exercise = generate_targeted_exercise(
        skill=skill,
        weaknesses=weaknesses,
        failed_criteria=failed_criteria,
    )

    return {
        "status": "adapted",
        "learner_id": learner.learner_id,
        "skill": skill,
        "score": score,
        "passed": passed,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "targeted_exercise": targeted_exercise,
        "next_action": (
            "Complete the targeted exercise, submit the attempt, "
            "and evaluate the new attempt."
        ),
    }


# ---------------------------------------------------------------------------
# LEARNER STATE
# ---------------------------------------------------------------------------

@mcp.tool()
def get_learner_state() -> dict:
    """
    Return the learner's current learning state.
    """

    return {
        "status": "retrieved",
        "learner": learner.to_dict(),
    }


# ---------------------------------------------------------------------------
# SERVER ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )