from fastapi.testclient import TestClient

import api.main as api_module


client = TestClient(api_module.app)


class FakeMCP:
    def __init__(self, response):
        self.response = response
        self.last_tool = None
        self.last_arguments = None

    async def call_tool(self, tool_name, arguments):
        self.last_tool = tool_name
        self.last_arguments = arguments
        return self.response


class FakeOrchestrator:
    response = {"status": "ok"}
    instances = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.mcp = FakeMCP(self.response)
        type(self).instances.append(self)

    @staticmethod
    def _extract_result(result):
        return result


def install_fake(monkeypatch, response):
    FakeOrchestrator.response = response
    FakeOrchestrator.instances = []
    monkeypatch.setattr(
        api_module,
        "LearningOrchestrator",
        FakeOrchestrator,
    )


def test_create_boss_fight(monkeypatch):
    expected = {
        "status": "created",
        "challenge": {"challenge_id": "boss-123", "state": "ready"},
    }
    install_fake(monkeypatch, expected)

    response = client.post(
        "/api/boss-fights",
        json={
            "learner_id": "api-test-learner",
            "skill": "python",
            "parent_mission_id": "build-number-guessing-game",
        },
    )

    assert response.status_code == 200
    assert response.json() == expected

    orchestrator = FakeOrchestrator.instances[-1]
    assert orchestrator.init_kwargs["learner_id"] == "api-test-learner"
    assert orchestrator.mcp.last_arguments["learner_id"] == "api-test-learner"


def test_start_boss_fight(monkeypatch):
    expected = {
        "status": "started",
        "challenge": {"challenge_id": "boss-123", "state": "in_progress"},
    }
    install_fake(monkeypatch, expected)

    response = client.post(
        "/api/boss-fights/boss-123/start",
        json={
            "learner_id": "api-test-learner",
            "skill": "python",
            "parent_mission_id": "build-number-guessing-game",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "started"


def test_evaluate_boss_fight(monkeypatch):
    expected = {
        "status": "evaluated",
        "challenge": {"challenge_id": "boss-123", "state": "passed"},
        "evaluation": {"score": 90, "passed": True},
    }
    install_fake(monkeypatch, expected)

    response = client.post(
        "/api/boss-fights/boss-123/evaluate",
        json={
            "learner_id": "api-test-learner",
            "skill": "python",
            "parent_mission_id": "build-number-guessing-game",
            "learner_response": "print('hello')",
            "attempt_type": "code",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "evaluated"


def test_get_boss_fight(monkeypatch):
    expected = {
        "status": "retrieved",
        "challenge": {"challenge_id": "boss-123", "state": "ready"},
    }
    install_fake(monkeypatch, expected)

    response = client.get(
        "/api/boss-fights/boss-123",
        params={
            "learner_id": "api-test-learner",
            "skill": "python",
            "parent_mission_id": "build-number-guessing-game",
        },
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_get_boss_fight_requires_parent_mission():
    response = client.get("/api/boss-fights/boss-123")

    assert response.status_code == 422


def test_list_boss_fights(monkeypatch):
    expected = {
        "status": "retrieved",
        "learner_id": "api-test-learner",
        "boss_fights": [],
        "count": 0,
    }
    install_fake(monkeypatch, expected)

    response = client.get(
        "/api/boss-fights",
        params={"learner_id": "api-test-learner", "skill": "python"},
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_unknown_challenge_maps_to_404(monkeypatch):
    install_fake(
        monkeypatch,
        {"status": "error", "message": "Challenge not found."},
    )

    response = client.post(
        "/api/boss-fights/missing/start",
        json={
            "learner_id": "api-test-learner",
            "skill": "python",
            "parent_mission_id": "build-number-guessing-game",
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]["message"].lower()


def test_invalid_challenge_state_maps_to_409(monkeypatch):
    install_fake(
        monkeypatch,
        {"status": "error", "message": "Challenge must be ready."},
    )

    response = client.post(
        "/api/boss-fights/boss-123/start",
        json={
            "learner_id": "api-test-learner",
            "skill": "python",
            "parent_mission_id": "build-number-guessing-game",
        },
    )

    assert response.status_code == 409


def test_invalid_attempt_type_is_rejected():
    response = client.post(
        "/api/boss-fights/boss-123/evaluate",
        json={
            "learner_id": "api-test-learner",
            "skill": "python",
            "parent_mission_id": "build-number-guessing-game",
            "learner_response": "some answer",
            "attempt_type": "audio",
        },
    )

    assert response.status_code == 422
