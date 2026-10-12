import shutil

import pytest

from content.course_catalog import get_mission_by_id
from services.assessment.assessment_service import AssessmentService
from services.assessment.javascript_code_validator import JavaScriptCodeValidator


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="Node.js is required for syntax checks.",
)
def test_validator_accepts_valid_javascript():
    result = JavaScriptCodeValidator.validate(
        "const greet = (name) => `Hello, ${name}`;\n"
    )
    assert result["syntax_valid"] is True
    assert result["validator_available"] is True
    assert result["error"] is None


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="Node.js is required for syntax checks.",
)
def test_validator_rejects_invalid_javascript():
    result = JavaScriptCodeValidator.validate("function broken( {\n")
    assert result["syntax_valid"] is False
    assert result["validator_available"] is True
    assert result["error"]


def test_empty_javascript_is_rejected():
    result = JavaScriptCodeValidator.validate("   ")
    assert result["syntax_valid"] is False


def test_missing_node_is_graceful(monkeypatch):
    monkeypatch.setattr(
        "services.assessment.javascript_code_validator.shutil.which",
        lambda _: None,
    )
    result = JavaScriptCodeValidator.validate("const answer = 42;")
    assert result["syntax_valid"] is None
    assert result["validator_available"] is False


class PassingBedrockEvaluator:
    def evaluate(self, mission, attempt):
        return {
            "score": 100,
            "passed": True,
            "criteria": [
                {
                    "id": criterion["id"],
                    "name": criterion["name"],
                    "passed": True,
                    "evidence": "Learner submission reviewed.",
                }
                for criterion in mission["criteria"]
            ],
            "strengths": [],
            "weaknesses": [],
            "feedback": "All criteria met.",
            "next_action": "Continue.",
        }


@pytest.mark.skipif(
    shutil.which("node") is None,
    reason="Node.js is required for syntax checks.",
)
def test_invalid_javascript_cannot_be_awarded_mastery():
    found = get_mission_by_id("build-product-inventory-manager")
    assert found is not None
    _, mission = found

    service = AssessmentService(
        bedrock_evaluator=PassingBedrockEvaluator()
    )
    evaluation = service.evaluate(
        mission,
        {
            "skill": "javascript",
            "attempt_type": "code",
            "learner_response": "function broken( {\n",
        },
    )

    assert evaluation["score"] == 0
    assert evaluation["passed"] is False
    assert all(
        not criterion["passed"]
        for criterion in evaluation["criteria"]
    )
    assert "syntax error" in evaluation["feedback"].lower()


def test_ground_truth_rejects_invalid_javascript_even_if_ai_passes():
    from services.assessment.ground_truth import GroundTruthEvaluator

    mission = {
        "criteria": [
            {"id": "example", "name": "Example requirement"},
        ],
    }

    evaluation = {
        "score": 100,
        "passed": True,
        "criteria": [
            {
                "id": "example",
                "name": "Example requirement",
                "passed": True,
                "evidence": "AI claims the submission is correct.",
            },
        ],
        "validation": {
            "javascript_syntax": {
                "syntax_valid": False,
                "error": "Unexpected token",
            },
        },
    }

    result = GroundTruthEvaluator().evaluate(mission, evaluation)

    assert result["score"] == 0
    assert result["passed"] is False
    assert result["status"] == "needs_practice"
    assert result["passed_criteria"] == 0
    assert all(not item["passed"] for item in result["criteria"])
