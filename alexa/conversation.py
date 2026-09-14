import asyncio
import json
from typing import Any

from agent.mcp_client import MCPLearningClient


class LearningConversation:
    """
    Stateful conversational learning journey.

    Alexa handles the conversational experience.
    MCP handles the learning operations.
    Bedrock provides reasoning and evidence.
    Ground Truth remains authoritative for mastery.
    """

    def __init__(
        self,
        skill: str,
        learner_level: str = "beginner",
    ) -> None:
        self.client = MCPLearningClient()

        self.skill = skill
        self.learner_level = learner_level

        self.goal: dict[str, Any] | None = None
        self.mission: dict[str, Any] | None = None
        self.attempt: dict[str, Any] | None = None
        self.evaluation: dict[str, Any] | None = None

    # =========================================================
    # STATE 1 — START LEARNING
    # =========================================================

    async def start(self) -> dict[str, Any]:
        """Create the learner's goal and first practical mission."""

        goal_result = await self.client.call_tool(
            "create_learning_goal",
            {
                "skill": self.skill,
                "learner_level": self.learner_level,
            },
        )

        self._raise_if_error(
            goal_result,
            "create_learning_goal",
        )

        self.goal = self._extract_json(goal_result)

        mission_result = await self.client.call_tool(
            "create_mission",
            {
                "skill": self.skill,
                "learner_level": self.learner_level,
            },
        )

        self._raise_if_error(
            mission_result,
            "create_mission",
        )

        mission_data = self._extract_json(
            mission_result
        )

        mission = mission_data.get("mission")

        if isinstance(mission, dict):
            self.mission = mission
        else:
            self.mission = {
                "title": mission_data.get(
                    "title",
                    "Practical Learning Mission",
                ),
                "description": mission_data.get(
                    "description",
                    "",
                ),
                "skills": mission_data.get(
                    "skills",
                    [],
                ),
            }

        return {
            "goal": self.goal,
            "mission": mission_data,
        }

    # =========================================================
    # STATE 2 — SUBMIT LEARNER WORK
    # =========================================================

    async def submit(
        self,
        learner_response: str,
        attempt_type: str = "code",
    ) -> dict[str, Any]:
        """Submit and record the learner's work."""

        if not self.mission:
            raise RuntimeError(
                "No active mission. "
                "Start the learning session first."
            )

        mission_text = self._mission_text()

        attempt_result = await self.client.call_tool(
            "submit_attempt",
            {
                "skill": self.skill,
                "mission": mission_text,
                "learner_response": learner_response,
                "attempt_type": attempt_type,
            },
        )

        self._raise_if_error(
            attempt_result,
            "submit_attempt",
        )

        self.attempt = self._extract_json(
            attempt_result
        )

        return {
            "attempt": self.attempt,
        }

    # =========================================================
    # STATE 3 — EVALUATE LEARNER WORK
    # =========================================================

    async def evaluate(
        self,
        learner_response: str,
        attempt_type: str = "code",
    ) -> dict[str, Any]:
        """
        Evaluate learner work using Bedrock and Ground Truth.

        Bedrock provides reasoning/evidence.
        Ground Truth determines authoritative mastery.
        """

        if not self.mission:
            raise RuntimeError(
                "No active mission. "
                "Start the learning session first."
            )

        mission_text = self._mission_text()

        evaluation_result = await self.client.call_tool(
            "evaluate_attempt",
            {
                "skill": self.skill,
                "mission": mission_text,
                "learner_response": learner_response,
                "attempt_type": attempt_type,
            },
        )

        self._raise_if_error(
            evaluation_result,
            "evaluate_attempt",
        )

        self.evaluation = self._extract_json(
            evaluation_result
        )

        return {
            "evaluation": self.evaluation,
        }

    # =========================================================
    # STATE 4 — ADAPT LEARNING
    # =========================================================

    async def continue_learning(self) -> dict[str, Any]:
        """
        Decide what the learner should do next.

        Mastered:
            Skip targeted remediation and advance difficulty.

        Needs practice:
            Identify weaknesses, generate targeted exercise,
            and adapt the next mission.
        """

        if not self.evaluation:
            raise RuntimeError(
                "No evaluation available. "
                "Evaluate a learner attempt first."
            )

        passed = bool(
            self.evaluation.get("passed", False)
        )

        score = self.evaluation.get(
            "score",
            0,
        )

        # -----------------------------------------------------
        # MASTERED PATH
        # -----------------------------------------------------

        if passed:
            adapted_result = await self.client.call_tool(
                "adapt_learning_mission",
                {
                    "skill": self.skill,
                    "evaluation": self.evaluation,
                },
            )

            self._raise_if_error(
                adapted_result,
                "adapt_learning_mission",
            )

            adapted_mission = self._extract_json(
                adapted_result
            )

            return {
                "status": "mastered",
                "score": score,
                "weaknesses": [],
                "targeted_exercise": None,
                "adapted_mission": adapted_mission,
                "message": (
                    "Excellent work. "
                    "You mastered this mission. "
                    "The next mission should increase the difficulty."
                ),
            }

        # -----------------------------------------------------
        # NEEDS-PRACTICE PATH
        # -----------------------------------------------------

        weaknesses_result = await self.client.call_tool(
            "identify_weaknesses",
            {
                "skill": self.skill,
                "evaluation": self.evaluation,
            },
        )

        self._raise_if_error(
            weaknesses_result,
            "identify_weaknesses",
        )

        weaknesses_data = self._extract_json(
            weaknesses_result
        )

        weakness_list = weaknesses_data.get(
            "weaknesses",
            [],
        )

        if not isinstance(weakness_list, list):
            weakness_list = []

        failed_criteria = weaknesses_data.get(
            "failed_criteria"
        )

        # -----------------------------------------------------
        # TARGETED EXERCISE
        # -----------------------------------------------------

        targeted_exercise = None

        if weakness_list:
            exercise_result = await self.client.call_tool(
                "generate_targeted_exercise",
                {
                    "skill": self.skill,
                    "weaknesses": weakness_list,
                    "failed_criteria": failed_criteria,
                },
            )

            self._raise_if_error(
                exercise_result,
                "generate_targeted_exercise",
            )

            targeted_exercise = self._extract_json(
                exercise_result
            )

        # -----------------------------------------------------
        # ADAPT NEXT MISSION
        # -----------------------------------------------------

        adapted_result = await self.client.call_tool(
            "adapt_learning_mission",
            {
                "skill": self.skill,
                "evaluation": self.evaluation,
            },
        )

        self._raise_if_error(
            adapted_result,
            "adapt_learning_mission",
        )

        adapted_mission = self._extract_json(
            adapted_result
        )

        return {
            "status": "needs_practice",
            "score": score,
            "weaknesses": weaknesses_data,
            "targeted_exercise": targeted_exercise,
            "adapted_mission": adapted_mission,
            "message": (
                "Let's strengthen the areas that need more practice."
            ),
        }

    # =========================================================
    # STATE 5 — LEARNER STATE
    # =========================================================

    async def learner_state(self) -> dict[str, Any]:
        """Return the learner's current learning state."""

        result = await self.client.call_tool(
            "get_learner_state",
            {},
        )

        self._raise_if_error(
            result,
            "get_learner_state",
        )

        return self._extract_json(result)

    # =========================================================
    # HELPERS
    # =========================================================

    def _mission_text(self) -> str:
        """Convert structured mission data into mission text."""

        if not self.mission:
            raise RuntimeError("No active mission.")

        title = self.mission.get(
            "title",
            "Learning Mission",
        )

        description = self.mission.get(
            "description",
            "",
        )

        skills = self.mission.get(
            "skills",
            [],
        )

        text = f"{title}\n\n{description}"

        if skills:
            text += "\n\nSkills:\n"

            for skill in skills:
                text += f"- {skill}\n"

        return text.strip()

    @staticmethod
    def _extract_text(result: Any) -> str:
        """Extract the first text payload from an MCP result."""

        if not result:
            return ""

        content = getattr(
            result,
            "content",
            None,
        )

        if not content:
            return ""

        for item in content:
            text = getattr(
                item,
                "text",
                None,
            )

            if text:
                return text

        return ""

    @classmethod
    def _extract_json(
        cls,
        result: Any,
    ) -> dict[str, Any]:
        """Extract JSON returned by an MCP tool."""

        text = cls._extract_text(result)

        if not text:
            return {}

        try:
            data = json.loads(text)

            if isinstance(data, dict):
                return data

            return {}

        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _raise_if_error(
        result: Any,
        tool_name: str,
    ) -> None:
        """Raise a useful error when an MCP tool fails."""

        if getattr(result, "isError", False):
            text = LearningConversation._extract_text(
                result
            )

            raise RuntimeError(
                f"MCP tool '{tool_name}' failed:\n{text}"
            )


# =============================================================
# DEMONSTRATION
# =============================================================

async def demo() -> None:
    print("=" * 60)
    print("MASTER IT BY DOING")
    print("STATEFUL LEARNING CONVERSATION")
    print("=" * 60)

    conversation = LearningConversation(
        skill="Python",
        learner_level="beginner",
    )

    # ---------------------------------------------------------
    # STATE 1 — START
    # ---------------------------------------------------------

    print("\nAlexa+:")
    print("Let's start your Python learning journey.")

    result = await conversation.start()

    print("\n[GOAL CREATED]")
    print(
        json.dumps(
            result["goal"],
            indent=2,
        )
    )

    print("\n[MISSION CREATED]")
    print(
        json.dumps(
            result["mission"],
            indent=2,
        )
    )

    print("\nAlexa+:")
    print(
        "Your mission is ready. "
        "Build the number guessing game "
        "and send me your solution."
    )

    # ---------------------------------------------------------
    # STATE 2 — LEARNER SUBMITS WORK
    # ---------------------------------------------------------

    learner_solution = """
import random

secret_number = random.randint(1, 10)

while True:
    guess = int(input("Guess the number: "))

    if guess == secret_number:
        print("Correct!")
        break
    elif guess < secret_number:
        print("Too low!")
    else:
        print("Too high!")
"""

    print("\nLearner:")
    print("Here is my Python solution.")

    submission = await conversation.submit(
        learner_response=learner_solution,
        attempt_type="code",
    )

    print("\n[ATTEMPT SUBMITTED]")
    print(
        json.dumps(
            submission["attempt"],
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # STATE 3 — EVALUATE
    # ---------------------------------------------------------

    print("\nAlexa+:")
    print(
        "I've received your solution. "
        "Let me evaluate it."
    )

    evaluation = await conversation.evaluate(
        learner_response=learner_solution,
        attempt_type="code",
    )

    print("\n[EVALUATION]")
    print(
        json.dumps(
            evaluation["evaluation"],
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # STATE 4 — ADAPT
    # ---------------------------------------------------------

    print("\nAlexa+:")
    print(
        "I've evaluated your work. "
        "Now I'll determine your next learning action."
    )

    adaptation = await conversation.continue_learning()

    print("\n[LEARNING ADAPTATION]")
    print(
        json.dumps(
            adaptation,
            indent=2,
        )
    )

    # ---------------------------------------------------------
    # STATE 5 — LEARNER STATE
    # ---------------------------------------------------------

    print("\nAlexa+:")
    print(
        adaptation["message"]
    )

    learner_state = await conversation.learner_state()

    print("\n[LEARNER STATE]")
    print(
        json.dumps(
            learner_state,
            indent=2,
        )
    )

    print("\n" + "=" * 60)
    print("FULL LEARNING CYCLE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo())
