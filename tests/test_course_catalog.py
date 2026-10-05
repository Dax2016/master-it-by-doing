from content.course_catalog import (
    COURSE_CATALOG,
    get_concept_for_mission,
    get_concepts,
    get_course,
    get_mission_by_id,
    get_missions,
)


def test_catalog_contains_python_javascript_and_aws_cloud():
    assert "python" in COURSE_CATALOG
    assert "javascript" in COURSE_CATALOG
    assert "aws-cloud" in COURSE_CATALOG


def test_python_has_three_missions():
    missions = get_missions("python")

    assert len(missions) == 3
    assert missions[0]["title"] == "Build a Number Guessing Game"
    assert missions[1]["title"] == "Build a Command-Line Quiz"
    assert missions[2]["title"] == "Build a Function-Based Expense Tracker"


def test_javascript_has_one_mission():
    missions = get_missions("javascript")

    assert len(missions) == 1
    assert missions[0]["title"] == "Build a Console To-Do List"


def test_skill_lookup_is_case_insensitive():
    course = get_course("Python")

    assert course is not None
    assert course["title"] == "Python Programming"


def test_unknown_skill_returns_no_missions():
    assert get_course("unknown-skill") is None
    assert get_missions("unknown-skill") == []


def test_aws_cloud_has_one_mission():
    missions = get_missions("aws-cloud")

    assert len(missions) == 1
    assert missions[0]["title"] == "Build a Serverless Hello World API"
    assert len(missions[0]["criteria"]) == 4

def test_skill_lookup_normalizes_human_friendly_names():
    course = get_course("AWS Cloud")

    assert course is not None
    assert course["id"] == "aws-cloud-computing"
    assert course["title"] == "AWS Cloud Computing"

def test_python_has_concepts():
    course = get_course("python")

    assert course is not None
    assert "concepts" in course
    assert len(course["concepts"]) == 6

    concept_ids = [concept["id"] for concept in course["concepts"]]

    assert concept_ids == [
        "python-variables",
        "python-input-output",
        "python-conditionals",
        "python-loops",
        "python-functions",
        "python-lists",
    ]

    concept = next(
        concept
        for concept in course["concepts"]
        if concept["id"] == "python-loops"
    )

    assert concept["id"] == "python-loops"
    assert concept["title"] == "Loops"
    assert "description" in concept
    assert "prerequisites" in concept
    assert "misconceptions" in concept


def test_python_missions_have_stable_ids():
    missions = get_missions("python")

    assert missions[0]["id"] == "build-number-guessing-game"
    assert missions[1]["id"] == "build-command-line-quiz"
    assert missions[2]["id"] == "build-expense-tracker"


def test_concept_references_existing_mission():
    course = get_course("python")

    assert course is not None

    concept = course["concepts"][0]
    mission_ids = {
        mission["id"]
        for mission in course["missions"]
    }

    assert set(concept["mission_ids"]).issubset(mission_ids)

def test_get_concepts_returns_python_concepts():
    concepts = get_concepts("python")

    assert len(concepts) == 6
    assert [concept["id"] for concept in concepts] == [
        "python-variables",
        "python-input-output",
        "python-conditionals",
        "python-loops",
        "python-functions",
        "python-lists",
    ]

def test_python_loop_concept_has_learning_content():
    concepts = get_concepts("python")

    concept = next(
        concept
        for concept in concepts
        if concept["id"] == "python-loops"
    )

    assert "examples" in concept
    assert "practice" in concept
    assert len(concept["examples"]) > 0
    assert len(concept["practice"]) > 0

def test_python_concepts_have_required_structure():
    concepts = get_concepts("python")

    required_fields = {
        "id",
        "title",
        "description",
        "prerequisites",
        "misconceptions",
        "examples",
        "practice",
        "mission_ids",
    }

    for concept in concepts:
        assert required_fields.issubset(concept.keys())

def test_all_concept_mission_references_are_valid():
    for course in COURSE_CATALOG.values():
        mission_ids = {
            mission["id"]
            for mission in course.get("missions", [])
        }

        for concept in course.get("concepts", []):
            assert set(concept.get("mission_ids", [])).issubset(mission_ids)

def test_all_concepts_have_learning_content():
    for course in COURSE_CATALOG.values():
        for concept in course.get("concepts", []):
            assert concept["description"].strip()
            assert len(concept["examples"]) > 0
            assert len(concept["practice"]) > 0
            assert len(concept["misconceptions"]) > 0


def test_get_concept_for_mission():
    concept = get_concept_for_mission(
        "python",
        "build-number-guessing-game",
    )

    assert concept is not None
    assert concept["id"] == "python-variables"
    assert concept["title"] == "Variables"

def test_get_concept_for_unknown_mission_returns_none():
    concept = get_concept_for_mission(
        "python",
        "unknown-mission",
    )

    assert concept is None

def test_get_mission_by_id_resolves_python_mission():
    result = get_mission_by_id(
        "build-number-guessing-game",
    )

    assert result is not None

    skill, mission = result

    assert skill == "python"
    assert mission["id"] == "build-number-guessing-game"
    assert mission["title"] == "Build a Number Guessing Game"


def test_get_mission_by_id_resolves_javascript_mission():
    result = get_mission_by_id(
        "build-console-to-do-list",
    )

    assert result is not None

    skill, mission = result

    assert skill == "javascript"
    assert mission["id"] == "build-console-to-do-list"
    assert mission["title"] == "Build a Console To-Do List"


def test_get_mission_by_id_resolves_aws_mission():
    result = get_mission_by_id(
        "build-serverless-hello-world-api",
    )

    assert result is not None

    skill, mission = result

    assert skill == "aws-cloud"
    assert mission["id"] == "build-serverless-hello-world-api"
    assert mission["title"] == "Build a Serverless Hello World API"


def test_get_mission_by_id_is_case_insensitive():
    result = get_mission_by_id(
        "BUILD-CONSOLE-TO-DO-LIST",
    )

    assert result is not None

    skill, mission = result

    assert skill == "javascript"
    assert mission["id"] == "build-console-to-do-list"


def test_get_mission_by_id_returns_none_for_unknown_mission():
    assert get_mission_by_id("unknown-mission") is None

def test_javascript_console_todo_mission_has_evaluation_criteria():
    result = get_mission_by_id(
        "build-console-to-do-list",
    )

    assert result is not None

    skill, mission = result

    assert skill == "javascript"

    criteria = mission["criteria"]

    assert len(criteria) == 5
    assert [criterion["id"] for criterion in criteria] == [
        "add_task",
        "view_tasks",
        "remove_task",
        "functions",
        "task_collection",
    ]

