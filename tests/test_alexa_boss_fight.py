import asyncio
import json
from types import SimpleNamespace

import pytest

from alexa import conversation as conversation_module


LEARNER_ID = "alexa-boss-fight-test-learner"
MISSION_ID = "build-number-guessing-game"
CHALLENGE_ID = "boss-fight-test-123"


def mcp_result(payload):
    return SimpleNamespace(
        content=[SimpleNamespace(text=json.dumps(payload))],
        isError=False,
    )


class FakeMCPClient:
    def __init__(self):
        self.calls = []
        self.challenge = {
            "id": CHALLENGE_ID,
            "skill": "python",
            "parent_mission_id": MISSION_ID,
            "status": "ready",
        }

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments.copy()))

        if name == "create_learning_goal":
            return mcp_result({"status": "created", "goal": {"skill": "python"}})
        if name == "create_mission":
            return mcp_result({
                "status": "created",
                "mission": {
                    "id": MISSION_ID,
                    "title": "Build a Number Guessing Game",
                    "description": "Build a playable guessing game.",
                    "skills": ["variables", "loops"],
                },
            })
        if name == "create_boss_fight":
            self.challenge = {**self.challenge, "status": "ready"}
            return mcp_result({"status": "created", "challenge": self.challenge})
        if name == "start_boss_fight":
            self.challenge = {**self.challenge, "status": "in_progress"}
            return mcp_result({"status": "started", "challenge": self.challenge})
        if name == "evaluate_boss_fight":
            evaluation = {
                "status": "evaluated",
                "passed": True,
                "score": 100,
                "boss_fight_id": CHALLENGE_ID,
            }
            self.challenge = {**self.challenge, "status": "passed"}
            return mcp_result({
                "status": "evaluated",
                "challenge": self.challenge,
                "evaluation": evaluation,
                "evidence": {"evidence_type": "boss_fight"},
            })
        if name == "get_boss_fight":
            return mcp_result({"status": "retrieved", "challenge": self.challenge})
        if name == "get_boss_fights":
            return mcp_result({
                "status": "retrieved",
                "learner_id": LEARNER_ID,
                "boss_fights": [self.challenge],
                "count": 1,
            })
        if name == "get_learner_state":
            return mcp_result({"status": "success", "learner": {"learner_id": LEARNER_ID}})
        return mcp_result({"status": "ok"})


@pytest.fixture
def conversation(monkeypatch):
    client = FakeMCPClient()
    monkeypatch.setattr(
        conversation_module,
        "MCPLearningClient",
        lambda: client,
    )
    instance = conversation_module.LearningConversation(
        skill="Python",
        learner_level="beginner",
        learner_id=LEARNER_ID,
    )
    return instance, client


async def _test_start_learning_propagates_identity_and_keeps_canonical_mission_id_async(conversation):
    instance, client = conversation

    await instance.start()

    assert instance.skill == "python"
    assert instance.mission["id"] == MISSION_ID
    assert client.calls[0] == (
        "create_learning_goal",
        {
            "skill": "python",
            "learner_level": "beginner",
            "learner_id": LEARNER_ID,
        },
    )
    assert client.calls[1] == (
        "create_mission",
        {
            "skill": "python",
            "learner_level": "beginner",
            "learner_id": LEARNER_ID,
        },
    )




def test_start_learning_propagates_identity_and_keeps_canonical_mission_id(conversation):
    asyncio.run(_test_start_learning_propagates_identity_and_keeps_canonical_mission_id_async(conversation))
async def _test_boss_fight_lifecycle_uses_same_identity_and_parent_async(conversation):
    instance, client = conversation
    await instance.start()

    created = await instance.create_boss_fight()
    started = await instance.start_boss_fight(CHALLENGE_ID)
    evaluated = await instance.evaluate_boss_fight(
        CHALLENGE_ID,
        "My completed number guessing game",
        attempt_type="code",
    )
    retrieved = await instance.get_boss_fight(CHALLENGE_ID)
    listed = await instance.get_boss_fights()

    assert created["status"] == "created"
    assert started["status"] == "started"
    assert evaluated["evaluation"]["passed"] is True
    assert retrieved["challenge"]["status"] == "passed"
    assert listed["count"] == 1

    boss_calls = [
        (name, args)
        for name, args in client.calls
        if name in {
            "create_boss_fight",
            "start_boss_fight",
            "evaluate_boss_fight",
            "get_boss_fight",
            "get_boss_fights",
        }
    ]
    assert len(boss_calls) == 5
    for name, args in boss_calls:
        assert args["learner_id"] == LEARNER_ID, name
        assert args["skill"] == "python", name
        if name != "get_boss_fights":
            assert args["parent_mission_id"] == MISSION_ID, name




def test_boss_fight_lifecycle_uses_same_identity_and_parent(conversation):
    asyncio.run(_test_boss_fight_lifecycle_uses_same_identity_and_parent_async(conversation))
async def _test_boss_fight_evaluation_does_not_overwrite_normal_evaluation_async(conversation):
    instance, _ = conversation
    await instance.start()
    normal_evaluation = {"status": "evaluated", "passed": False, "score": 50}
    instance.evaluation = normal_evaluation

    await instance.create_boss_fight()
    await instance.start_boss_fight(CHALLENGE_ID)
    await instance.evaluate_boss_fight(CHALLENGE_ID, "Finished project")

    assert instance.evaluation is normal_evaluation
    assert instance.boss_fight_evaluation["passed"] is True




def test_boss_fight_evaluation_does_not_overwrite_normal_evaluation(conversation):
    asyncio.run(_test_boss_fight_evaluation_does_not_overwrite_normal_evaluation_async(conversation))
async def _test_boss_fight_requires_canonical_parent_mission_id_async(conversation):
    instance, client = conversation

    with pytest.raises(RuntimeError, match="canonical parent_mission_id"):
        await instance.create_boss_fight()

    assert client.calls == []




def test_boss_fight_requires_canonical_parent_mission_id(conversation):
    asyncio.run(_test_boss_fight_requires_canonical_parent_mission_id_async(conversation))
async def _test_boss_fight_tool_status_errors_raise_async(conversation):
    instance, client = conversation
    await instance.start()

    async def error_call(name, arguments):
        client.calls.append((name, arguments.copy()))
        return mcp_result({
            "status": "error",
            "message": "Unknown mission ID",
        })

    instance.client.call_tool = error_call

    with pytest.raises(RuntimeError, match="Unknown mission ID"):
        await instance.create_boss_fight()




def test_boss_fight_tool_status_errors_raise(conversation):
    asyncio.run(_test_boss_fight_tool_status_errors_raise_async(conversation))
def test_empty_learner_id_is_rejected(monkeypatch):
    monkeypatch.setattr(
        conversation_module,
        "MCPLearningClient",
        lambda: FakeMCPClient(),
    )

    with pytest.raises(ValueError, match="learner_id"):
        conversation_module.LearningConversation(
            skill="python",
            learner_id="   ",
        )
