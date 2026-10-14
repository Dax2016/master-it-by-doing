from services.learner.learner_state import LearnerState


def achievement(skill, achievement_id="boss-fight-first-victory"):
    return {
        "achievement_id": achievement_id,
        "title": "Boss Fight: First Victory",
        "skill": skill,
        "evidence_id": f"evidence-{skill}",
    }


def test_achievement_is_awarded_once_per_canonical_skill():
    learner = LearnerState("achievement-test")

    assert learner.award_achievement(achievement("AWS-Cloud")) is True
    assert learner.award_achievement(achievement("aws_cloud")) is False
    assert len(learner.achievements) == 1


def test_same_achievement_can_be_earned_in_another_skill():
    learner = LearnerState("achievement-test")

    assert learner.award_achievement(achievement("AWS-Cloud")) is True
    assert learner.award_achievement(achievement("Python")) is True
    assert learner.award_achievement(achievement("JavaScript")) is True
    assert len(learner.achievements) == 3


def test_profile_filters_achievements_by_skill():
    learner = LearnerState("achievement-test")
    learner.award_achievement(achievement("AWS-Cloud"))
    learner.award_achievement(achievement("Python"))

    aws_profile = learner.get_learner_profile(skill="aws_cloud")
    python_profile = learner.get_learner_profile(skill="Python")

    assert [item["skill"] for item in aws_profile["achievements"]] == [
        "AWS-Cloud"
    ]
    assert [item["skill"] for item in python_profile["achievements"]] == [
        "Python"
    ]


def test_achievement_does_not_complete_or_master_a_mission():
    learner = LearnerState("achievement-test")
    learner.award_achievement(achievement("AWS-Cloud"))

    assert learner.completed_missions == []
    assert learner.capabilities == []
    assert learner.mastery == {}


def test_achievement_is_in_serialized_learner_state():
    learner = LearnerState("achievement-test")
    learner.award_achievement(achievement("AWS-Cloud"))

    serialized = learner.to_dict()
    assert len(serialized["achievements"]) == 1
    assert serialized["achievements"][0]["skill"] == "AWS-Cloud"


def test_achievement_requires_id_and_skill():
    import pytest

    learner = LearnerState("achievement-test")

    with pytest.raises(ValueError):
        learner.award_achievement({"skill": "Python"})

    with pytest.raises(ValueError):
        learner.award_achievement({
            "achievement_id": "boss-fight-first-victory"
        })
