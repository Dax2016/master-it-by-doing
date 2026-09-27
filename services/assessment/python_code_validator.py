import ast
from typing import Any


class PythonCodeValidator:
    """Deterministically validate Python source and mission evidence."""

    @staticmethod
    def validate(
        source: str,
        mission: str | None = None,
    ) -> dict[str, Any]:
        """Return deterministic syntax and structural evidence."""

        if not isinstance(source, str) or not source.strip():
            return {
                "syntax_valid": False,
                "error": "Python source is empty.",
                "criteria": {},
            }

        try:
            tree = ast.parse(source)

        except SyntaxError as exc:
            location = (
                f"line {exc.lineno}"
                if exc.lineno
                else "unknown line"
            )

            return {
                "syntax_valid": False,
                "error": (
                    f"Python syntax error at {location}: "
                    f"{exc.msg}"
                ),
                "criteria": {},
            }

        criteria = {}

        normalized_mission = (
            str(mission or "")
            .strip()
            .lower()
        )

        if normalized_mission == "build a command-line quiz":
            criteria = PythonCodeValidator._validate_quiz(
                tree
            )

        return {
            "syntax_valid": True,
            "error": None,
            "criteria": criteria,
        }

    @staticmethod
    def _validate_quiz(tree: ast.AST) -> dict[str, bool]:
        """Deterministically detect Command-Line Quiz requirements."""

        nodes = list(ast.walk(tree))

        has_questions = any(
            isinstance(node, (ast.List, ast.Tuple))
            and len(getattr(node, "elts", [])) >= 2
            for node in nodes
        )

        has_input = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "input"
            for node in nodes
        )

        has_answer_comparison = any(
            isinstance(node, ast.Compare)
            and any(
                isinstance(operator, ast.Eq)
                for operator in node.ops
            )
            for node in nodes
        )

        has_score_variable = any(
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Store)
            and node.id == "score"
            for node in nodes
        )

        has_score_increment = any(
            isinstance(node, ast.AugAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "score"
            for node in nodes
        )

        has_loop = any(
            isinstance(node, (ast.For, ast.While))
            for node in nodes
        )

        has_print = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
            for node in nodes
        )

        return {
            "quiz_questions": (
                has_questions
                and has_input
            ),
            "answer_checking": (
                has_input
                and has_answer_comparison
            ),
            "score_tracking": (
                has_score_variable
                and has_score_increment
            ),
            "multiple_questions": has_loop,
            "final_score": has_print and has_score_variable,
        }
