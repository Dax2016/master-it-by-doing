from content.course_catalog import (
    COURSE_CATALOG,
    get_concepts,
    get_course,
    get_missions,
)


def test_catalog_contains_python_javascript_and_aws_cloud():
    assert "python" in COURSE_CATALOG
    assert "javascript" in COURSE_CATALOG
    assert "aws-cloud" in COURSE_CATALOG


def test_python_has_two_missions():
    missions = get_missions("python")

    assert len(missions) == 2
    assert missions[0]["title"] == "Build a Number Guessing Game"
    assert missions[1]["title"] == "Build a Command-Line Quiz"


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
    assert len(course["concepts"]) > 0

    concept = course["concepts"][0]

    assert concept["id"] == "python-loops"
    assert concept["title"] == "Loops"
    assert "description" in concept
    assert "prerequisites" in concept
    assert "misconceptions" in concept

def test_python_missions_have_stable_ids():
    missions = get_missions("python")

    assert missions[0]["id"] == "build-number-guessing-game"
    assert missions[1]["id"] == "build-command-line-quiz"


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

    assert len(concepts) == 1
    assert concepts[0]["id"] == "python-loops"
    assert concepts[0]["title"] == "Loops"

def test_python_loop_concept_has_learning_content():
    concepts = get_concepts("python")

    concept = concepts[0]

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
