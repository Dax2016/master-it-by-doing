from content.course_catalog import COURSE_CATALOG, get_course, get_missions


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
