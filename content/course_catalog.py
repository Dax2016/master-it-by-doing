COURSE_CATALOG = {
    "python": {
        "id": "python-programming",
        "title": "Python Programming",
        "difficulty": "beginner",
        "description": (
            "Build practical Python programs while developing "
            "core programming skills."
        ),
        "missions": [
            {
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
            {
                "title": "Build a Command-Line Quiz",
                "description": (
                    "Create a Python quiz program that asks multiple questions, "
                    "checks the learner's answers, tracks the score, and "
                    "displays the final result."
                ),
                "skills": [
                    "Variables",
                    "Input and output",
                    "Conditionals",
                    "Loops",
                    "Functions",
                    "Lists",
                ],
            },
        ],
    },
    "javascript": {
        "id": "javascript-development",
        "title": "JavaScript Development",
        "difficulty": "beginner",
        "description": (
            "Build practical JavaScript applications while developing "
            "core programming skills."
        ),
        "missions": [
            {
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
        ],
    },
}


def get_course(skill: str) -> dict | None:
    """Return the course definition for a skill."""
    return COURSE_CATALOG.get(skill.strip().lower())


def get_missions(skill: str) -> list[dict]:
    """Return the ordered missions for a skill."""
    course = get_course(skill)

    if course is None:
        return []

    return course["missions"]
