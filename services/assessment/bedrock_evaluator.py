import json
import os
from typing import Any

import boto3


DEFAULT_MODEL_ID = "us.amazon.nova-2-lite-v1:0"
DEFAULT_REGION = "us-east-1"


class BedrockEvaluator:
    """
    AI-powered learner attempt evaluator.

    Bedrock is responsible for reasoning about the learner's attempt.
    This service is responsible for converting that reasoning into the
    application's controlled evaluation contract.
    """

    def __init__(
        self,
        model_id: str | None = None,
        region_name: str | None = None,
    ) -> None:
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID",
            DEFAULT_MODEL_ID,
        )

        self.region_name = region_name or os.getenv(
            "AWS_REGION",
            DEFAULT_REGION,
        )

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region_name,
        )

    def evaluate(
        self,
        mission: dict[str, Any],
        attempt: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate a learner attempt using Amazon Bedrock.
        """

        prompt = self._build_prompt(mission, attempt)

        response = self.client.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt,
                        }
                    ],
                }
            ],
        )

        raw_text = self._extract_text(response)

        evaluation = self._parse_evaluation(raw_text)

        return self._validate_evaluation(evaluation)

    def _build_prompt(
        self,
        mission: dict[str, Any],
        attempt: dict[str, Any],
    ) -> str:
        """
        Build a strict evaluation prompt.

        The model must return JSON only.
        """

        mission_json = json.dumps(
            mission,
            ensure_ascii=False,
            indent=2,
        )

        attempt_json = json.dumps(
            attempt,
            ensure_ascii=False,
            indent=2,
        )

        return f"""
You are the assessment engine for Master It By Doing.

Your job is to evaluate a learner's actual attempt against the mission
requirements.

Do not teach the learner.
Do not rewrite the learner's work.
Do not invent requirements that are not present in the mission.

Evaluate only the evidence contained in the learner attempt.

MISSION:
{mission_json}

LEARNER ATTEMPT:
{attempt_json}

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
  "score": 0,
  "passed": false,
  "criteria": [
        {{
      "id": "criterion_id",
      "name": "criterion name",
      "passed": false,
      "evidence": "brief evidence from the attempt"
        }}
  ],
  "strengths": [],
  "weaknesses": [],
  "feedback": "concise evidence-based feedback",
  "next_action": "specific recommended next learning action"
}}

Rules:

1. score must be an integer from 0 to 100.
2. passed must be true only when the learner demonstrates the required
   mission skills.
3. criteria must correspond to the mission requirements.
4. Each criterion must include the exact criterion id provided by the mission.
5. Never invent, rename, or omit a criterion id.
6. strengths must contain only demonstrated strengths.
7. weaknesses must contain only demonstrated weaknesses.
8. feedback must be concise and evidence-based.
9. next_action must address the most important next learning step.
10. Do not expose internal reasoning.
11. Do not include markdown.
12. Return JSON only.
""".strip()

    @staticmethod
    def _extract_text(response: dict[str, Any]) -> str:
        """
        Extract the assistant's text from a Bedrock Converse response.
        """

        try:
            return response["output"]["message"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Bedrock returned an unexpected response structure."
            ) from exc

    @staticmethod
    def _parse_evaluation(raw_text: str) -> dict[str, Any]:
        """
        Parse the model response into a Python dictionary.
        """

        cleaned = raw_text.strip()

        # Handle an occasional fenced JSON response defensively.
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        try:
            evaluation = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Bedrock evaluator returned invalid JSON."
            ) from exc

        if not isinstance(evaluation, dict):
            raise ValueError(
                "Bedrock evaluator must return a JSON object."
            )

        return evaluation

    @staticmethod
    def _validate_evaluation(
        evaluation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate and normalize the application-facing contract.
        """

        required_fields = {
            "score",
            "passed",
            "criteria",
            "strengths",
            "weaknesses",
            "feedback",
            "next_action",
        }

        missing = required_fields - evaluation.keys()

        if missing:
            raise ValueError(
                f"Bedrock evaluation is missing fields: {sorted(missing)}"
            )

        score = evaluation["score"]

        if not isinstance(score, int) or isinstance(score, bool):
            raise ValueError("Evaluation score must be an integer.")

        if not 0 <= score <= 100:
            raise ValueError("Evaluation score must be between 0 and 100.")

        if not isinstance(evaluation["passed"], bool):
            raise ValueError("Evaluation passed field must be boolean.")

        for field in (
            "criteria",
            "strengths",
            "weaknesses",
        ):
            if not isinstance(evaluation[field], list):
                raise ValueError(
                    f"Evaluation field '{field}' must be a list."
                )

        for field in (
            "feedback",
            "next_action",
        ):
            if not isinstance(evaluation[field], str):
                raise ValueError(
                    f"Evaluation field '{field}' must be a string."
                )

        return {
            "score": score,
            "passed": evaluation["passed"],
            "criteria": evaluation["criteria"],
            "strengths": evaluation["strengths"],
            "weaknesses": evaluation["weaknesses"],
            "feedback": evaluation["feedback"],
            "next_action": evaluation["next_action"],
        }