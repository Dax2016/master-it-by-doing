from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_get_learning_profile():
    response = client.get(
        "/api/learning/profile",
        params={
            "learner_id": "api-profile-test",
            "skill": "Python",
            "level": "beginner",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["learner_id"] == "api-profile-test"
    assert data["skill"] == "Python"
    assert data["level"] == "beginner"

    assert "profile" in data

    profile = data["profile"]

    assert profile["learner_id"] == "api-profile-test"
    assert "current" in profile
    assert "demonstrated" in profile
    assert "mastery" in profile
    assert "strengths" in profile
    assert "weaknesses" in profile
    assert "next" in profile
