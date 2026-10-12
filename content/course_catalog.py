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
                    "Design and implement a Lambda handler that returns a JSON "
                    "response. Document how API Gateway invokes it, provide the "
                    "configuration or code, and show a representative test "
                    "request and response. Clearly distinguish local evidence "
                    "from resources actually deployed in AWS."
                ),
                "skills": [
                    "AWS Lambda",
                    "Amazon API Gateway",
                    "JSON",
                    "Serverless architecture",
                    "Cloud deployment",
                ],
                "criteria": [
                    {"id": "lambda_function", "name": "Create an AWS Lambda function"},
                    {"id": "json_response", "name": "Return a JSON response from the Lambda function"},
                    {"id": "api_gateway", "name": "Explain or configure how API Gateway invokes the Lambda function"},
                    {"id": "api_test", "name": "Test the handler or deployed endpoint and verify the expected response"},
                ],
            },
            {
                "id": "build-event-driven-order-notification",
                "title": "Build an Event-Driven Order Notification",
                "description": (
                    "Design an event-driven order notification workflow. Submit "
                    "a sample order event, a Lambda handler that processes it, "
                    "and an explanation or configuration showing how Amazon SQS "
                    "or EventBridge triggers processing. Include success and "
                    "failure handling, plus a sample event and expected result. "
                    "Do not claim deployment without deployment evidence."
                ),
                "skills": [
                    "Amazon EventBridge",
                    "Amazon SQS",
                    "AWS Lambda",
                    "Event-driven architecture",
                    "Error handling",
                ],
                "criteria": [
                    {"id": "order_event", "name": "Define a structured order event with the required order details"},
                    {"id": "event_source", "name": "Explain or configure an event source using SQS or EventBridge"},
                    {"id": "lambda_processing", "name": "Process the order event in a Lambda handler"},
                    {"id": "notification_result", "name": "Produce a clear notification result for a successfully processed order"},
                    {"id": "failure_handling", "name": "Describe or implement handling for invalid events or processing failures"},
                ],
            },
            {
                "id": "secure-and-troubleshoot-serverless-api",
                "title": "Secure and Troubleshoot a Serverless API",
                "description": (
                    "Review a serverless API design and improve its security "
                    "and diagnostics. Provide a least-privilege IAM policy "
                    "example, request validation, appropriate HTTP error "
                    "responses, and a troubleshooting plan using CloudWatch "
                    "logs and metrics. Explain how you would verify each "
                    "change, without exposing secrets."
                ),
                "skills": [
                    "AWS IAM",
                    "Least privilege",
                    "Amazon API Gateway",
                    "Amazon CloudWatch",
                    "API validation",
                    "Troubleshooting",
                ],
                "criteria": [
                    {"id": "least_privilege", "name": "Provide an IAM policy limited to the permissions the API requires"},
                    {"id": "request_validation", "name": "Validate incoming requests and handle invalid input"},
                    {"id": "http_errors", "name": "Return appropriate HTTP status codes and safe error messages"},
                    {"id": "observability", "name": "Describe or configure useful CloudWatch logs and monitoring"},
                    {"id": "troubleshooting", "name": "Provide a reproducible troubleshooting and verification plan"},
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
                    "view, and remove tasks. Use an array to store tasks, "
                    "functions to organize operations, and input validation "
                    "to handle invalid choices."
                ),
                "skills": [
                    "Variables",
                    "Arrays",
                    "Functions",
                    "Conditionals",
                    "Loops",
                ],
                "criteria": [
                    {"id": "add_task", "name": "Allow the user to add a task"},
                    {"id": "view_tasks", "name": "Display the current tasks"},
                    {"id": "remove_task", "name": "Allow the user to remove a task"},
                    {"id": "functions", "name": "Use functions to organize task operations"},
                    {"id": "task_collection", "name": "Store and update tasks in an array"},
                ],
            },
            {
                "id": "build-product-inventory-manager",
                "title": "Build a Product Inventory Manager",
                "description": (
                    "Build a JavaScript inventory program that stores products "
                    "as objects in an array. Implement functions to add a "
                    "product, search by name or ID, update stock, remove a "
                    "product, and display the current inventory. Validate "
                    "inputs and explain how duplicate IDs are handled."
                ),
                "skills": [
                    "JavaScript objects",
                    "Arrays",
                    "Functions",
                    "Array methods",
                    "Input validation",
                ],
                "criteria": [
                    {"id": "product_model", "name": "Represent products with objects containing stable identifiers and relevant fields"},
                    {"id": "add_product", "name": "Add a product to the inventory"},
                    {"id": "search_product", "name": "Find a product using its name or identifier"},
                    {"id": "update_stock", "name": "Update product stock and reject invalid quantities"},
                    {"id": "remove_product", "name": "Remove a selected product from the inventory"},
                    {"id": "display_inventory", "name": "Display the current inventory using organized functions"},
                ],
            },
            {
                "id": "build-async-api-dashboard",
                "title": "Build an Async API Dashboard",
                "description": (
                    "Create a small JavaScript dashboard that retrieves data "
                    "from a public or supplied JSON API using fetch and "
                    "async/await. Display the returned data and implement "
                    "visible loading, empty, and error states. Explain how "
                    "HTTP failures and network errors are handled."
                ),
                "skills": [
                    "fetch",
                    "Promises",
                    "async/await",
                    "JSON",
                    "HTTP responses",
                    "Error handling",
                ],
                "criteria": [
                    {"id": "fetch_data", "name": "Request data from a JSON API using fetch"},
                    {"id": "async_await", "name": "Use async/await to manage the asynchronous request"},
                    {"id": "render_data", "name": "Parse and display useful fields from the returned JSON data"},
                    {"id": "loading_state", "name": "Show a loading state while the request is in progress"},
                    {"id": "error_state", "name": "Handle HTTP failures and network errors with a useful error state"},
                    {"id": "empty_state", "name": "Handle an empty or missing data result gracefully"},
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
def get_courses() -> list[dict]:
    """Return the available learning paths from the course catalog."""

    return [
        {
            "skill": skill,
            "id": course.get("id", skill),
            "title": course.get("title", skill),
            "difficulty": course.get("difficulty", "beginner"),
            "description": course.get("description", ""),
            "mission_count": len(course.get("missions", [])),
        }
        for skill, course in COURSE_CATALOG.items()
    ]
