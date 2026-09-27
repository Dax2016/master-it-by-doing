from typing import Any


class GroundTruthEvaluator:
    """
    Deterministic validation layer for learner evaluations.

    Ground Truth owns objective criterion results when deterministic
    validation evidence is available. Bedrock provides evidence,
    reasoning, strengths, weaknesses, and feedback.
    """

    def evaluate(
        self,
        mission: dict[str, Any],
        evaluation: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate an evaluation against deterministic requirements."""

        criteria = evaluation.get("criteria", [])

        if not isinstance(criteria, list):
            raise ValueError(
                "Evaluation criteria must be a list."
            )

        required_criteria = self.get_required_criteria(
            mission
        )

        deterministic_criteria = self._get_deterministic_criteria(
            evaluation
        )

        results = []

        for required in required_criteria:
            result = self._validate_criterion(
                required,
                criteria,
                deterministic_criteria,
            )
            results.append(result)

        passed_count = sum(
            1
            for result in results
            if result["passed"]
        )

        total_count = len(results)

        final_passed = (
            total_count > 0
            and passed_count == total_count
        )

        final_score = (
            round(
                (passed_count / total_count) * 100
            )
            if total_count
            else 0
        )

        return {
            "passed": final_passed,
            "score": final_score,
            "criteria": results,
            "passed_criteria": passed_count,
            "total_criteria": total_count,
            "status": (
                "mastered"
                if final_passed
                else "needs_practice"
            ),
        }

    @staticmethod
    def _get_deterministic_criteria(
        evaluation: dict[str, Any],
    ) -> dict[str, bool]:
        """
        Extract authoritative criterion results from deterministic
        validation evidence when available.
        """

        validation = evaluation.get("validation")

        if not isinstance(validation, dict):
            return {}

        python_syntax = validation.get("python_syntax")

        if not isinstance(python_syntax, dict):
            return {}

        if python_syntax.get("syntax_valid") is not True:
            return {}

        criteria = python_syntax.get("criteria")

        if not isinstance(criteria, dict):
            return {}

        return {
            str(criterion_id): value is True
            for criterion_id, value in criteria.items()
        }

    @staticmethod
    def get_required_criteria(
        mission: dict[str, Any],
    ) -> list[dict[str, str]]:
        """
        Determine the authoritative requirements for a mission.

        Ground Truth owns these requirements. AI evaluation provides
        evidence against them, but does not define them.
        """

        mission_title = (
            mission.get("mission")
            or mission.get("title")
            or ""
        ).strip().lower()

        # Python — Number Guessing Game
        if mission_title == "build a number guessing game":
            return [
                {
                    "id": "random_number",
                    "name": (
                        "Generate a random number "
                        "between 1 and 10"
                    ),
                },
                {
                    "id": "user_input",
                    "name": (
                        "Prompt user for a guess"
                    ),
                },
                {
                    "id": "feedback",
                    "name": (
                        "Compare guess to the number "
                        "and provide appropriate feedback"
                    ),
                },
                {
                    "id": "multiple_attempts",
                    "name": (
                        "Allow multiple guessing attempts "
                        "until correct"
                    ),
                },
            ]

        # Python — Command-Line Quiz
        if mission_title == "build a command-line quiz":
            return [
                {
                    "id": "quiz_questions",
                    "name": (
                        "Ask multiple quiz questions"
                    ),
                },
                {
                    "id": "answer_checking",
                    "name": (
                        "Check whether each answer is correct"
                    ),
                },
                {
                    "id": "score_tracking",
                    "name": (
                        "Track the learner's score"
                    ),
                },
                {
                    "id": "multiple_questions",
                    "name": (
                        "Process multiple questions in a loop"
                    ),
                },
                {
                    "id": "final_score",
                    "name": (
                        "Display the final quiz score"
                    ),
                },
            ]

        # Python — Authenticated REST API
        if mission_title == "build an authenticated api":
            return [
                {
                    "id": "rest_api",
                    "name": (
                        "Create a REST API using Python"
                    ),
                },
                {
                    "id": "authentication",
                    "name": (
                        "Implement authentication "
                        "for protected endpoints"
                    ),
                },
                {
                    "id": "crud_resources",
                    "name": (
                        "Allow authenticated users to create, "
                        "read, update, and delete resources"
                    ),
                },
                {
                    "id": "http_status_codes",
                    "name": (
                        "Return appropriate HTTP status codes"
                    ),
                },
                {
                    "id": "documentation",
                    "name": (
                        "Document how another developer can "
                        "run and test the API"
                    ),
                },
            ]

        # Generic mission fallback
        skills = mission.get("skills", [])

        if not isinstance(skills, list):
            return []

        return [
            {
                "id": f"skill_{index}",
                "name": str(skill),
            }
            for index, skill in enumerate(skills)
            if str(skill).strip()
        ]

    @staticmethod
    def _validate_criterion(
        required_criterion: dict[str, str],
        ai_criteria: list[dict[str, Any]],
        deterministic_criteria: dict[str, bool],
    ) -> dict[str, Any]:
        """
        Validate one criterion.

        Deterministic validation takes precedence when an authoritative
        result exists. Otherwise, Bedrock's criterion result is used.
        """

        required_id = required_criterion["id"]
        required_name = required_criterion["name"]

        normalized_required = (
            required_name.strip().lower()
        )

        # ---------------------------------------------------------------
        # Deterministic result takes precedence over AI pass/fail.
        # ---------------------------------------------------------------

        if required_id in deterministic_criteria:
            for criterion in ai_criteria:
                if not isinstance(criterion, dict):
                    continue

                if criterion.get("id") == required_id:
                    evidence = str(
                        criterion.get("evidence", "")
                    )

                    return {
                        "id": required_id,
                        "name": required_name,
                        "passed": deterministic_criteria[
                            required_id
                        ],
                        "evidence": evidence,
                    }

            return {
                "id": required_id,
                "name": required_name,
                "passed": deterministic_criteria[
                    required_id
                ],
                "evidence": (
                    "Deterministic Python validation "
                    "verified this criterion."
                ),
            }

        # ---------------------------------------------------------------
        # Fall back to AI evidence when deterministic validation does
        # not provide a result for this criterion.
        # ---------------------------------------------------------------

        for criterion in ai_criteria:
            if not isinstance(criterion, dict):
                continue

            if criterion.get("id") == required_id:
                return {
                    "id": required_id,
                    "name": required_name,
                    "passed": (
                        criterion.get("passed") is True
                    ),
                    "evidence": str(
                        criterion.get("evidence", "")
                    ),
                }

            name = str(
                criterion.get("name", "")
            ).strip().lower()

            if name == normalized_required:
                return {
                    "id": required_id,
                    "name": required_name,
                    "passed": (
                        criterion.get("passed") is True
                    ),
                    "evidence": str(
                        criterion.get("evidence", "")
                    ),
                }

        return {
            "id": required_id,
            "name": required_name,
            "passed": False,
            "evidence": (
                "No matching evidence was returned "
                "for this required criterion."
            ),
        }
