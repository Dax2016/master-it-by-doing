from services.learner.learner_state import LearnerState


def test_empty_learner_profile():
    learner = LearnerState("profile-test")

    profile = learner.get_learner_profile()

    assert profile["learner_id"] == "profile-test"

    assert profile["current"]["goal"] is None
    assert profile["current"]["active_mission"] is None

    assert profile["demonstrated"]["capabilities"] == []
    assert profile["demonstrated"]["completed_missions"] == []
    assert profile["demonstrated"]["evidence_count"] == 0

    assert profile["mastery"]["mastered"] == []
    assert profile["mastery"]["developing"] == []
    assert profile["mastery"]["needs_practice"] == []

    assert profile["strengths"] == []
    assert profile["weaknesses"] == []

    assert profile["next"]["mission"] is None


def test_learner_profile_includes_current_learning_state():
    learner = LearnerState("profile-test")

    goal = {
        "id": "goal-1",
        "skill": "Python",
        "learner_level": "beginner",
        "status": "active",
    }

    mission = {
        "id": "build-number-guessing-game",
        "title": "Build a Number Guessing Game",
        "description": "Create a Python number guessing game.",
        "skill": "Python",
    }

    learner.add_goal(goal)
    learner.set_active_mission(mission, skill="Python")

    profile = learner.get_learner_profile()

    assert profile["current"]["goal"] == goal
    assert profile["current"]["active_mission"]["mission_id"] == (
        "build-number-guessing-game"
    )
    assert profile["current"]["active_mission"]["status"] == "in_progress"


def test_learner_profile_includes_demonstrated_capabilities():
    learner = LearnerState("profile-test")

    learner.add_evidence({
        "id": "evidence-1",
        "learner_id": "profile-test",
        "mission_id": "build-number-guessing-game",
    })

    learner.add_capability({
        "learner_id": "profile-test",
        "mission_id": "build-number-guessing-game",
        "skill": "Python",
        "score": 100,
        "evidence_ids": ["evidence-1"],
        "concept_ids": ["loops", "functions"],
        "demonstrated_criteria": [
            {"id": "loops", "name": "Loops"},
        ],
    })

    profile = learner.get_learner_profile()

    assert len(profile["demonstrated"]["capabilities"]) == 1

    capability = profile["demonstrated"]["capabilities"][0]

    assert capability["skill"] == "Python"
    assert capability["missions"] == 1
    assert capability["best_score"] == 100
    assert "evidence-1" in capability["evidence_ids"]
    assert "loops" in capability["concept_ids"]


def test_learner_profile_classifies_mastery():
    learner = LearnerState("profile-test")

    learner.record_mastery(
        skill="Python",
        mission="Build a Number Guessing Game",
        status="mastered",
        score=100,
        passed=True,
        passed_criteria=4,
        total_criteria=4,
        evidence={"id": "evidence-mastered"},
    )

    learner.record_mastery(
        skill="Python",
        mission="Build a Command Line Quiz",
        status="needs_practice",
        score=50,
        passed=False,
        passed_criteria=2,
        total_criteria=4,
        evidence={"id": "evidence-practice"},
    )

    profile = learner.get_learner_profile()

    assert len(profile["mastery"]["mastered"]) == 1
    assert len(profile["mastery"]["needs_practice"]) == 1
    assert profile["mastery"]["developing"] == []

    mastered = profile["mastery"]["mastered"][0]

    assert mastered["skill"] == "Python"
    assert mastered["mission"] == "Build a Number Guessing Game"
    assert mastered["status"] == "mastered"

    needs_practice = profile["mastery"]["needs_practice"][0]

    assert needs_practice["skill"] == "Python"
    assert needs_practice["mission"] == "Build a Command Line Quiz"
    assert needs_practice["status"] == "needs_practice"


def test_learner_profile_includes_strengths_and_weaknesses():
    learner = LearnerState("profile-test")

    learner.update_skill_profile(
        strengths=["Variables", "Functions"],
        weaknesses=["Loops"],
    )

    profile = learner.get_learner_profile()

    assert profile["strengths"] == ["Variables", "Functions"]
    assert profile["weaknesses"] == ["Loops"]


def test_learner_profile_is_read_only():
    learner = LearnerState("profile-test")

    goal = {
        "id": "goal-1",
        "skill": "Python",
        "learner_level": "beginner",
        "status": "active",
    }

    learner.add_goal(goal)

    before_goals = list(learner.goals)
    before_active_mission = learner.active_mission
    before_capabilities = list(learner.capabilities)
    before_mastery = dict(learner.mastery)

    learner.get_learner_profile()

    assert learner.goals == before_goals
    assert learner.active_mission == before_active_mission
    assert learner.capabilities == before_capabilities
    assert learner.mastery == before_mastery

def test_active_practice_is_persisted_and_cleared():
    learner = LearnerState("practice-test")

    practice = {
        "parent_mission_id": "build-expense-tracker",
        "parent_mission": "Build a Function-Based Expense Tracker",
        "exercise": {
            "title": "Build a Guessing Game Core",
        },
        "targeted_criteria": ["total_expense_function"],
        "targeted_skills": ["functions"],
        "status": "ready",
    }

    learner.set_active_practice(practice)

    assert learner.active_practice == practice
    assert learner.to_dict()["active_practice"] == practice

    learner.clear_active_practice()

    assert learner.active_practice is None
    assert learner.to_dict()["active_practice"] is None
