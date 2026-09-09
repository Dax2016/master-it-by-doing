from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Master It By Doing")


@mcp.tool()
def create_learning_goal(
    skill: str,
    learner_level: str = "beginner",
) -> dict:
    """
    Create a practical learning goal for the learner.

    Args:
        skill: The skill the learner wants to learn.
        learner_level: The learner's current level.
    """
    return {
        "status": "created",
        "skill": skill,
        "learner_level": learner_level,
        "message": (
            f"Learning goal created: learn {skill} "
            f"at {learner_level} level."
        ),
        "next_action": "Create a practical learning mission.",
    }


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
        "next_action": "Complete the mission and submit the attempt.",
    }


@mcp.tool()
def submit_attempt(
    skill: str,
    mission: str,
    learner_response: str,
    attempt_type: str = "text",
) -> dict:
    """
    Submit a learner's work for evaluation.

    Args:
        skill: The skill being practiced.
        mission: The mission the learner was assigned.
        learner_response: The learner's actual work or answer.
        attempt_type: The type of submission: code, text, or answer.
    """
    valid_attempt_types = {"code", "text", "answer"}

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
            "message": "learner_response cannot be empty.",
        }

    return {
        "status": "submitted",
        "skill": skill,
        "mission": mission,
        "attempt_type": normalized_type,
        "learner_response": learner_response,
        "next_action": "Evaluate the learner's attempt.",
    }


@mcp.tool()
def evaluate_attempt(
    skill: str,
    mission: str,
    learner_response: str,
    attempt_type: str = "text",
) -> dict:
    """
    Evaluate a learner's submitted work against a practical mission.

    Args:
        skill: The skill being practiced.
        mission: The mission the learner was assigned.
        learner_response: The learner's actual work or answer.
        attempt_type: The type of submission: code, text, or answer.
    """
    valid_attempt_types = {"code", "text", "answer"}

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
            "message": "learner_response cannot be empty.",
        }

    response = learner_response.strip()

    # Mission-specific evaluation criteria.
    if (
        skill.strip().lower() == "python"
        and "number guessing" in mission.strip().lower()
    ):
        criteria = [
            {
                "name": "Random number generation",
                "passed": (
                    "random" in response.lower()
                    and "randint" in response.lower()
                ),
            },
            {
                "name": "Learner input",
                "passed": "input(" in response.lower(),
            },
            {
                "name": "Guess comparison",
                "passed": (
                    "==" in response
                    or "!=" in response
                    or "<" in response
                    or ">" in response
                ),
            },
            {
                "name": "Conditional logic",
                "passed": "if " in response.lower(),
            },
            {
                "name": "Result feedback",
                "passed": (
                    "print(" in response.lower()
                    or "return " in response.lower()
                ),
            },
            {
                "name": "Python implementation",
                "passed": (
                    "import " in response.lower()
                    or "input(" in response.lower()
                ),
            },
        ]
    else:
        # Generic fallback until AI-powered evaluation is introduced.
        criteria = [
            {
                "name": "Practical implementation",
                "passed": len(response) >= 100,
            },
            {
                "name": "Relevant response",
                "passed": len(response.split()) >= 10,
            },
        ]

    passed_criteria = [
        criterion["name"]
        for criterion in criteria
        if criterion["passed"]
    ]

    failed_criteria = [
        criterion["name"]
        for criterion in criteria
        if not criterion["passed"]
    ]

    total_criteria = len(criteria)
    passed_count = len(passed_criteria)

    score = round((passed_count / total_criteria) * 100)
    passed = score >= 80

    if passed:
        feedback = (
            "The learner demonstrated the required practical skills "
            "for this mission."
        )
        next_action = "Create a targeted follow-up mission."
    else:
        feedback = (
            "The learner has not yet demonstrated all required skills. "
            "Focus the next exercise on the missing criteria."
        )
        next_action = (
            "Create a targeted exercise for the identified weaknesses."
        )

    return {
        "status": "evaluated",
        "skill": skill,
        "mission": mission,
        "attempt_type": normalized_type,
        "score": score,
        "passed": passed,
        "criteria": criteria,
        "strengths": passed_criteria,
        "weaknesses": failed_criteria,
        "feedback": feedback,
        "next_action": next_action,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")