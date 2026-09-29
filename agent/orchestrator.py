"""
Master It By Doing
Agent Orchestrator

Coordinates the learner journey through the real MCP learning engine.

Architecture:

Learner
    ↓
Agent Orchestrator
    ↓
MCP Client
    ↓
MCP Server
    ↓
Master It By Doing Learning Engine
    ↓
Assessment / Ground Truth / Learner State
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from agent.mcp_client import MCPLearningClient
from content.course_catalog import get_missions


@dataclass
class LearnerSession:
    """State for a single learner session."""

    learner_id: str
    skill: str
    level: str

    goal: Optional[Dict[str, Any]] = None
    mission: Optional[Dict[str, Any]] = None

    latest_attempt: Optional[Dict[str, Any]] = None
    attempt_text: Optional[str] = None
    attempt_type: str = "text"

    evaluation: Optional[Dict[str, Any]] = None
    weaknesses: Optional[Dict[str, Any]] = None

    targeted_exercise: Optional[Dict[str, Any]] = None
    adapted_mission: Optional[Dict[str, Any]] = None


class LearningOrchestrator:
    """
    Coordinates the learner journey through MCP.

    The orchestrator controls workflow sequencing.

    Learning rules, assessment logic, Ground Truth,
    learner state, and adaptation remain inside the
    Master It By Doing learning engine.
    """

    def __init__(
        self,
        learner_id: str,
        skill: str,
        level: str,
        mission: Optional[str] = None,
        mcp_client: Optional[MCPLearningClient] = None,
    ):
        """
        Create a learner orchestration session.

        If a mission is supplied, it becomes the active mission
        for this session. This is important for web/API requests
        where the learner is submitting work against a specific
        mission.

        If no mission is supplied, the orchestrator will create
        one through the MCP learning engine when the learning
        cycle begins.
        """

        self.session = LearnerSession(
            learner_id=learner_id,
            skill=skill,
            level=level,
            mission=(
                next(
                    (
                        {
                            **catalog_mission,
                            "mission": catalog_mission["title"],
                            "skill": skill,
                        }
                        for catalog_mission in get_missions(skill)
                        if catalog_mission.get("title", "").strip().lower()
                        == mission.strip().lower()
                    ),
                    {
                        "mission": mission.strip(),
                        "skill": skill,
                    },
                )
                if mission and mission.strip()
                else None
            ),
        )

        self.mcp = mcp_client or MCPLearningClient()

    # ============================================================
    # MCP OPERATIONS
    # ============================================================

    async def create_learning_goal(self) -> Any:
        """Create the learner's practical learning goal."""

        result = await self.mcp.call_tool(
            "create_learning_goal",
            {
                "skill": self.session.skill,
                "learner_level": self.session.level,
            },
        )

        self.session.goal = self._extract_result(result)

        return result

    async def create_mission(self) -> Any:
        """
        Create the learner's practical mission.

        This is only called when a mission was not supplied
        when the orchestrator session was created.
        """

        result = await self.mcp.call_tool(
            "create_mission",
            {
                "skill": self.session.skill,
                "learner_level": self.session.level,
            },
        )

        self.session.mission = self._extract_result(result)

        return result

    async def submit_attempt(
        self,
        attempt: str,
        attempt_type: str = "code",
    ) -> Any:
        """Submit the learner's work."""

        if not attempt or not attempt.strip():
            raise ValueError(
                "Attempt cannot be empty."
            )

        mission_text = self._mission_text()

        if not mission_text:
            raise ValueError(
                "Cannot submit an attempt without an active mission."
            )

        self.session.attempt_text = attempt
        self.session.attempt_type = attempt_type

        result = await self.mcp.call_tool(
            "submit_attempt",
            {
                "skill": self.session.skill,
                "mission": mission_text,
                "learner_response": attempt,
                "attempt_type": attempt_type,
            },
        )

        self.session.latest_attempt = self._extract_result(result)

        return result

    async def evaluate_attempt(self) -> Any:
        """
        Evaluate the learner's latest attempt.

        Bedrock performs analysis.
        Ground Truth determines authoritative evaluation.
        """

        if not self.session.attempt_text:
            raise ValueError(
                "Cannot evaluate an attempt before one has been submitted."
            )

        mission_text = self._mission_text()

        if not mission_text:
            raise ValueError(
                "Cannot evaluate an attempt without an active mission."
            )

        result = await self.mcp.call_tool(
            "evaluate_attempt",
            {
                "skill": self.session.skill,
                "mission": mission_text,
                "learner_response": self.session.attempt_text,
                "attempt_type": self.session.attempt_type,
            },
        )

        self.session.evaluation = self._extract_result(result)

        return result

    async def identify_weaknesses(self) -> Any:
        """Identify weaknesses from the evaluation."""

        if self.session.evaluation is None:
            raise ValueError(
                "Cannot identify weaknesses before evaluating an attempt."
            )

        result = await self.mcp.call_tool(
            "identify_weaknesses",
            {
                "skill": self.session.skill,
                "evaluation": self.session.evaluation,
            },
        )

        self.session.weaknesses = self._extract_result(result)

        return result

    async def generate_targeted_exercise(self) -> Any:
        """Generate an exercise targeting learner weaknesses."""

        if self.session.weaknesses is None:
            raise ValueError(
                "Cannot generate a targeted exercise before "
                "identifying weaknesses."
            )

        weaknesses = self._weakness_list()

        if not weaknesses:
            self.session.targeted_exercise = None

            return {
                "status": "skipped",
                "message": (
                    "No weaknesses were identified. "
                    "Targeted exercise generation skipped."
                ),
            }

        result = await self.mcp.call_tool(
            "generate_targeted_exercise",
            {
                "skill": self.session.skill,
                "weaknesses": weaknesses,
                "failed_criteria": self._failed_criteria(),
            },
        )

        self.session.targeted_exercise = self._extract_result(result)

        return result

    async def adapt_learning_mission(self) -> Any:
        """Adapt the mission using the latest evaluation."""

        if self.session.evaluation is None:
            raise ValueError(
                "Cannot adapt a mission before evaluating an attempt."
            )

        result = await self.mcp.call_tool(
            "adapt_learning_mission",
            {
                "skill": self.session.skill,
                "evaluation": self.session.evaluation,
            },
        )

        self.session.adapted_mission = self._extract_result(result)

        return result

    async def get_learner_state(self) -> Any:
        """Retrieve the learner's current state."""

        result = await self.mcp.call_tool(
            "get_learner_state",
            {},
        )

        return self._extract_result(result)

    # ============================================================
    # COMPLETE LEARNING CYCLE
    # ============================================================

    async def run_learning_cycle(
        self,
        attempt: Optional[str] = None,
        attempt_type: str = "code",
    ) -> Dict[str, Any]:
        """
        Execute the complete adaptive learning cycle.

        Workflow:

            GOAL
              ↓
            MISSION
              ↓
            DO
              ↓
            SUBMIT
              ↓
            EVALUATE
              ↓
            IDENTIFY WEAKNESSES
              ↓
            TARGETED EXERCISE (only if weaknesses exist)
              ↓
            ADAPT
        """

        # --------------------------------------------------------
        # GOAL
        # --------------------------------------------------------

        if self.session.goal is None:
            await self.create_learning_goal()

        # --------------------------------------------------------
        # MISSION
        # --------------------------------------------------------

        # If the caller supplied a mission when constructing
        # the orchestrator, preserve it.
        #
        # Otherwise create a mission through MCP.
        if self.session.mission is None:
            await self.create_mission()

        # --------------------------------------------------------
        # SUBMIT ATTEMPT
        # --------------------------------------------------------

        if attempt is not None:
            await self.submit_attempt(
                attempt=attempt,
                attempt_type=attempt_type,
            )

        # --------------------------------------------------------
        # EVALUATION + ADAPTATION
        # --------------------------------------------------------

        if self.session.attempt_text is not None:
            await self.evaluate_attempt()
            await self.identify_weaknesses()

            # Targeted practice is only meaningful when
            # actual weaknesses have been identified.
            if self._weakness_list():
                await self.generate_targeted_exercise()
            else:
                self.session.targeted_exercise = None

            await self.adapt_learning_mission()

        return self.get_state()

    # ============================================================
    # TEST / STATE RECORDING METHODS
    # ============================================================

    def record_goal(
        self,
        goal: Dict[str, Any],
    ) -> None:
        """Record a goal directly for tests or restored state."""

        self.session.goal = goal

    def record_mission(
        self,
        mission: Dict[str, Any],
    ) -> None:
        """Record a mission directly for tests or restored state."""

        self.session.mission = mission

    def record_attempt(
        self,
        attempt: Dict[str, Any],
    ) -> None:
        """Record an attempt directly for tests or restored state."""

        self.session.latest_attempt = attempt

        attempt_text = (
            attempt.get("learner_response")
            or attempt.get("attempt")
            or attempt.get("code")
            or attempt.get("response")
            or attempt.get("answer")
        )

        if attempt_text is not None:
            self.session.attempt_text = str(
                attempt_text
            )

        attempt_type = attempt.get("attempt_type")

        if attempt_type:
            self.session.attempt_type = attempt_type

    def record_evaluation(
        self,
        evaluation: Dict[str, Any],
    ) -> None:
        """Record an evaluation directly."""

        self.session.evaluation = evaluation

    def record_weaknesses(
        self,
        weaknesses: Dict[str, Any],
    ) -> None:
        """Record weaknesses directly."""

        self.session.weaknesses = weaknesses

    def record_targeted_exercise(
        self,
        targeted_exercise: Dict[str, Any],
    ) -> None:
        """Record a targeted exercise directly."""

        self.session.targeted_exercise = targeted_exercise

    def record_adapted_mission(
        self,
        adapted_mission: Dict[str, Any],
    ) -> None:
        """Record an adapted mission directly."""

        self.session.adapted_mission = adapted_mission

    # ============================================================
    # ORCHESTRATION STATE
    # ============================================================

    def next_action(self) -> str:
        """Return the next action required in the learning cycle."""

        if self.session.goal is None:
            return "create_learning_goal"

        if self.session.mission is None:
            return "create_mission"

        if self.session.latest_attempt is None:
            return "submit_attempt"

        if self.session.evaluation is None:
            return "evaluate_attempt"

        if self.session.weaknesses is None:
            return "identify_weaknesses"

        # A targeted exercise is only part of the workflow
        # when actual weaknesses exist.
        if self._weakness_list():
            if self.session.targeted_exercise is None:
                return "generate_targeted_exercise"

        if self.session.adapted_mission is None:
            return "adapt_learning_mission"

        return "continue_learning"

    def get_state(self) -> Dict[str, Any]:
        """Return the complete current orchestration state."""

        return {
            "learner_id": self.session.learner_id,
            "skill": self.session.skill,
            "level": self.session.level,
            "goal": self.session.goal,
            "mission": self.session.mission,
            "latest_attempt": self.session.latest_attempt,
            "attempt_text": self.session.attempt_text,
            "attempt_type": self.session.attempt_type,
            "evaluation": self.session.evaluation,
            "weaknesses": self.session.weaknesses,
            "targeted_exercise": self.session.targeted_exercise,
            "adapted_mission": self.session.adapted_mission,
            "next_action": self.next_action(),
        }

    # ============================================================
    # MCP RESPONSE NORMALIZATION
    # ============================================================

    @classmethod
    def _extract_result(
        cls,
        result: Any,
    ) -> Dict[str, Any]:
        """
        Convert an MCP CallToolResult into the actual
        structured JSON payload returned by the server.

        MCP commonly returns:

            content=[
                TextContent(
                    text='{"status": "..."}'
                )
            ]

        We parse the JSON text instead of passing
        the MCP wrapper into downstream tools.
        """

        # --------------------------------------------------------
        # Structured content
        # --------------------------------------------------------

        if hasattr(result, "structuredContent"):

            structured = result.structuredContent

            if isinstance(structured, dict):
                return structured

        if hasattr(result, "structured_content"):

            structured = result.structured_content

            if isinstance(structured, dict):
                return structured

        # --------------------------------------------------------
        # Standard MCP content blocks
        # --------------------------------------------------------

        if hasattr(result, "content"):

            content = result.content

            if isinstance(content, list):

                text_parts: List[str] = []

                for item in content:

                    if hasattr(item, "text"):

                        text = item.text

                        if text:
                            text_parts.append(
                                str(text)
                            )

                    elif isinstance(item, dict):

                        text = item.get("text")

                        if text:
                            text_parts.append(
                                str(text)
                            )

                # Most MCP tools return exactly one
                # JSON document inside one text block.
                for text in text_parts:

                    parsed = cls._parse_json(text)

                    if isinstance(parsed, dict):
                        return parsed

                # If JSON parsing failed, preserve
                # the returned text.
                if text_parts:

                    return {
                        "content": text_parts,
                    }

        # --------------------------------------------------------
        # Direct dictionary
        # --------------------------------------------------------

        if isinstance(result, dict):
            return result

        # --------------------------------------------------------
        # Final fallback
        # --------------------------------------------------------

        return {
            "mcp_result": result,
        }

    @staticmethod
    def _parse_json(
        text: str,
    ) -> Any:
        """Safely parse JSON returned by an MCP text response."""

        if not isinstance(text, str):
            return text

        text = text.strip()

        if not text:
            return text

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            return text

    # ============================================================
    # DATA EXTRACTION HELPERS
    # ============================================================

    def _mission_text(self) -> str:
        """
        Extract the actual mission text from the structured
        mission stored in the learner session.
        """

        mission = self.session.mission

        if mission is None:
            return ""

        if isinstance(mission, str):
            return mission.strip()

        if not isinstance(mission, dict):
            return str(mission).strip()

        mission_data = mission.get("mission")

        # --------------------------------------------------------
        # Mission stored as structured object
        # --------------------------------------------------------

        if isinstance(mission_data, dict):

            title = mission_data.get(
                "title",
                "",
            )

            description = mission_data.get(
                "description",
                "",
            )

            if title and description:
                return (
                    f"{title}: {description}"
                )

            if description:
                return str(
                    description
                ).strip()

            if title:
                return str(
                    title
                ).strip()

            return json.dumps(
                mission_data,
                ensure_ascii=False,
            )

        # --------------------------------------------------------
        # Mission stored directly as a string
        # --------------------------------------------------------

        if isinstance(mission_data, str):
            return mission_data.strip()

        # --------------------------------------------------------
        # Other supported mission formats
        # --------------------------------------------------------

        for key in (
            "description",
            "task",
            "challenge",
            "title",
        ):

            value = mission.get(key)

            if value is not None:

                value = str(value).strip()

                if value:
                    return value

        # --------------------------------------------------------
        # Final fallback
        # --------------------------------------------------------

        return json.dumps(
            mission,
            ensure_ascii=False,
        )

    def _weakness_list(self) -> List[str]:
        """Normalize weaknesses into a list of strings."""

        weaknesses = self.session.weaknesses

        if weaknesses is None:
            return []

        if isinstance(weaknesses, str):
            return [weaknesses]

        if isinstance(weaknesses, list):
            return [
                str(item)
                for item in weaknesses
            ]

        if isinstance(weaknesses, dict):

            value = weaknesses.get(
                "weaknesses"
            )

            if isinstance(value, list):

                return [
                    str(item)
                    for item in value
                ]

            if isinstance(value, str):
                return [value]

            value = weaknesses.get(
                "items"
            )

            if isinstance(value, list):

                return [
                    str(item)
                    for item in value
                ]

        return [
            str(weaknesses)
        ]

    def _failed_criteria(
        self,
    ) -> List[Dict[str, Any]]:
        """Extract failed criteria from the evaluation."""

        evaluation = self.session.evaluation

        if not isinstance(
            evaluation,
            dict,
        ):
            return []

        # --------------------------------------------------------
        # Explicit failed_criteria
        # --------------------------------------------------------

        failed = evaluation.get(
            "failed_criteria"
        )

        if isinstance(
            failed,
            list,
        ):

            return [
                item
                for item in failed
                if isinstance(
                    item,
                    dict,
                )
            ]

        # --------------------------------------------------------
        # Derive failures from criteria
        # --------------------------------------------------------

        criteria = evaluation.get(
            "criteria"
        )

        if isinstance(
            criteria,
            list,
        ):

            failed_items: List[
                Dict[str, Any]
            ] = []

            for criterion in criteria:

                if not isinstance(
                    criterion,
                    dict,
                ):
                    continue

                if criterion.get(
                    "passed"
                ) is False:

                    failed_items.append(
                        criterion
                    )

            return failed_items

        return []

    # ============================================================
    # GENERAL HELPERS
    # ============================================================

    @staticmethod
    def _result_to_text(
        value: Any,
    ) -> str:
        """Convert an arbitrary result value to text."""

        if value is None:
            return ""

        if isinstance(
            value,
            str,
        ):
            return value

        return str(value)



