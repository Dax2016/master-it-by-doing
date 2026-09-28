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
                "criteria": [
                    {
                        "id": "random_number",
                        "name": "Generate a random number between 1 and 10",
                    },
                    {
                        "id": "user_input",
                        "name": "Prompt user for a guess",
                    },
                    {
                        "id": "feedback",
                        "name": (
                            "Compare guess to the number "
                            "and provide appropriate feedback"
                        ),
                    },
                    {
                        "id": "multiple_attempts",
                        "name": (
                            "Allow multiple guessing attempts "
                            "until correct"
                        ),
                    },
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
                "criteria": [
                    {
                        "id": "quiz_questions",
                        "name": "Ask multiple quiz questions",
                    },
                    {
                        "id": "answer_checking",
                        "name": "Check whether each answer is correct",
                    },
                    {
                        "id": "score_tracking",
                        "name": "Track the learner's score",
                    },
                    {
                        "id": "multiple_questions",
                        "name": "Process multiple questions in a loop",
                    },
                    {
                        "id": "final_score",
                        "name": "Display the final quiz score",
                    },
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
