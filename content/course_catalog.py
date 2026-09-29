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
    "aws-cloud": {
        "id": "aws-cloud-computing",
        "title": "AWS Cloud Computing",
        "difficulty": "beginner",
        "description": (
            "Build practical cloud applications using core AWS services "
            "and serverless architecture."
        ),
        "missions": [
            {
                "title": "Build a Serverless Hello World API",
                "description": (
                    "Create an AWS Lambda function that returns a JSON response "
                    "and expose it through Amazon API Gateway."
                ),
                "skills": [
                    "AWS Lambda",
                    "Amazon API Gateway",
                    "JSON",
                    "Serverless architecture",
                    "Cloud deployment",
                ],
                "criteria": [
                    {
                        "id": "lambda_function",
                        "name": "Create an AWS Lambda function",
                    },
                    {
                        "id": "json_response",
                        "name": "Return a JSON response from the Lambda function",
                    },
                    {
                        "id": "api_gateway",
                        "name": "Expose the Lambda function through API Gateway",
                    },
                    {
                        "id": "api_test",
                        "name": "Test the API endpoint and verify the expected response",
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
    normalized_skill = (
        skill.strip()
        .lower()
        .replace(" ", "-")
    )

    return COURSE_CATALOG.get(normalized_skill)


def get_missions(skill: str) -> list[dict]:
    """Return the ordered missions for a skill."""
    course = get_course(skill)

    if course is None:
        return []

    return course["missions"]
