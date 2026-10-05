COURSE_CATALOG = {
    "python": {
        "id": "python-programming",
        "title": "Python Programming",
        "difficulty": "beginner",
        "description": (
            "Build practical Python programs while developing "
            "core programming skills."
        ),
        "concepts": [
            {
                "id": "python-variables",
                "title": "Variables",
                "description": (
                    "Store and update values that a program needs "
                    "to process information."
                ),
                "prerequisites": [],
                "misconceptions": [
                    "A variable can only store one type of value.",
                    "Variables cannot be updated after assignment.",
                ],
                "examples": [
                    "Store a user's name in a variable.",
                    "Update a running score stored in a variable.",
                ],
                "practice": [
                    "Create variables for a user's name and score.",
                    "Update a variable after processing input.",
                ],
                "mission_ids": [
                    "build-number-guessing-game",
                    "build-command-line-quiz",
                    "build-expense-tracker",
                ],
            },
            {
                "id": "python-input-output",
                "title": "Input and Output",
                "description": (
                    "Receive information from users and present "
                    "useful results through program output."
                ),
                "prerequisites": [],
                "misconceptions": [
                    "Input is automatically converted to numbers.",
                    "Output can only display text.",
                ],
                "examples": [
                    "Use input to collect a user's response.",
                    "Use print to display a calculated result.",
                ],
                "practice": [
                    "Ask a user for a value and display it.",
                    "Display a formatted result after processing input.",
                ],
                "mission_ids": [
                    "build-number-guessing-game",
                    "build-command-line-quiz",
                    "build-expense-tracker",
                ],
            },
            {
                "id": "python-conditionals",
                "title": "Conditionals",
                "description": (
                    "Use conditions to make decisions and control "
                    "which actions a program performs."
                ),
                "prerequisites": [],
                "misconceptions": [
                    "An if statement always needs an else branch.",
                    "Conditions can only compare numbers.",
                ],
                "examples": [
                    "Check whether a user's answer is correct.",
                    "Choose different feedback based on a condition.",
                ],
                "practice": [
                    "Write a condition that compares two values.",
                    "Display different messages for different outcomes.",
                ],
                "mission_ids": [
                    "build-number-guessing-game",
                    "build-command-line-quiz",
                ],
            },
            {
                "id": "python-loops",
                "title": "Loops",
                "description": (
                    "Use loops to repeat actions and process multiple "
                    "iterations of a task."
                ),
                "prerequisites": [],
                "misconceptions": [
                    "A loop always runs forever.",
                    "A loop is only useful for numbers.",
                ],
                "examples": [
                    "Use a for loop to process each item in a list.",
                    "Use a while loop to repeat until a condition is met.",
                ],
                "practice": [
                    "Write a loop that prints the numbers 1 through 10.",
                    "Write a loop that keeps asking for input until the user enters quit.",
                ],
                "mission_ids": [
                    "build-number-guessing-game",
                    "build-command-line-quiz",
                    "build-expense-tracker",
                ],
            },
            {
                "id": "python-functions",
                "title": "Functions",
                "description": (
                    "Organize reusable program logic into functions "
                    "that can accept inputs and return results."
                ),
                "prerequisites": [],
                "misconceptions": [
                    "Every function must accept an argument.",
                    "A function cannot return a calculated value.",
                ],
                "examples": [
                    "Create a function that calculates a total.",
                    "Use a function to perform a reusable task.",
                ],
                "practice": [
                    "Write a function that accepts an argument.",
                    "Write a function that returns a calculated result.",
                ],
                "mission_ids": [
                    "build-number-guessing-game",
                    "build-command-line-quiz",
                    "build-expense-tracker",
                ],
            },
            {
                "id": "python-lists",
                "title": "Lists",
                "description": (
                    "Store and process collections of related values "
                    "using Python lists."
                ),
                "prerequisites": [],
                "misconceptions": [
                    "A list can contain only numbers.",
                    "List elements cannot be changed.",
                ],
                "examples": [
                    "Store multiple quiz questions in a list.",
                    "Store multiple expenses in a list.",
                ],
                "practice": [
                    "Create a list and add several values.",
                    "Loop through a list and process each item.",
                ],
                "mission_ids": [
                    "build-command-line-quiz",
                    "build-expense-tracker",
                ],
            },
        ],
        "missions": [

            {
                "id": "build-number-guessing-game",
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
                    "id": "build-command-line-quiz",
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
            {
                "id": "build-expense-tracker",
                "title": "Build a Function-Based Expense Tracker",
                "description": (
                    "Create a Python program that lets the learner add expenses, "
                    "calculate the total, and display the recorded expenses "
                    "using reusable functions."
                ),
                "skills": [
                    "Variables",
                    "Input and output",
                    "Lists",
                    "Loops",
                    "Functions",
                ],
                "criteria": [
                    {
                        "id": "expense_storage",
                        "name": "Store multiple expenses in a list",
                    },
                    {
                        "id": "add_expense_function",
                        "name": "Use a function to add an expense",
                    },
                    {
                        "id": "total_expense_function",
                        "name": "Use a function to calculate the total expenses",
                    },
                    {
                        "id": "multiple_expenses",
                        "name": "Process multiple expenses using a loop",
                    },
                    {
                        "id": "expense_summary",
                        "name": "Display the expenses and calculated total",
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
            "id": "build-serverless-hello-world-api",
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
                "id": "build-console-to-do-list",
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
                "criteria": [
                    {
                        "id": "add_task",
                        "name": "Allow the user to add a task",
                    },
                    {
                        "id": "view_tasks",
                        "name": "Display the current tasks",
                    },
                    {
                        "id": "remove_task",
                        "name": "Allow the user to remove a task",
                    },
                    {
                        "id": "functions",
                        "name": "Use functions to organize task operations",
                    },
                    {
                        "id": "task_collection",
                        "name": "Store and update tasks in an array",
                    },
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


def get_mission_by_id(mission_id: str) -> tuple[str, dict] | None:
    """Return the course skill and mission definition for a mission ID."""
    normalized_id = mission_id.strip().lower()

    if not normalized_id:
        return None

    for skill, course in COURSE_CATALOG.items():
        for mission in course.get("missions", []):
            if mission.get("id", "").strip().lower() == normalized_id:
                return skill, mission

    return None


def get_concepts(skill: str) -> list[dict]:
    """Return the concepts for a skill."""
    course = get_course(skill)

    if course is None:
        return []

    return course.get("concepts", [])


def get_concepts_for_mission(
    skill: str,
    mission_id: str,
) -> list[dict]:
    """Return all concepts associated with a mission ID."""

    concepts = get_concepts(skill)

    return [
        concept
        for concept in concepts
        if mission_id in concept.get("mission_ids", [])
    ]


def get_concept_for_mission(
    skill: str,
    mission_id: str,
) -> dict | None:
    """Return the concept associated with a mission ID."""
    concepts = get_concepts(skill)

    for concept in concepts:
        if mission_id in concept.get("mission_ids", []):
            return concept

    return None