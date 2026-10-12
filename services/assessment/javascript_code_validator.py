import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class JavaScriptCodeValidator:
    """Check JavaScript syntax with Node.js without executing learner code."""

    @staticmethod
    def validate(source: str) -> dict[str, Any]:
        source = str(source or "")

        if not source.strip():
            return {
                "syntax_valid": False,
                "validator_available": True,
                "error": "JavaScript source is empty.",
            }

        node_binary = os.environ.get("NODE_BINARY", "node")
        resolved_node = shutil.which(node_binary)

        if resolved_node is None and Path(node_binary).is_file():
            resolved_node = node_binary

        if resolved_node is None:
            return {
                "syntax_valid": None,
                "validator_available": False,
                "error": (
                    "Node.js is unavailable. JavaScript syntax "
                    "could not be verified."
                ),
            }

        file_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".js",
                encoding="utf-8",
                delete=False,
            ) as source_file:
                source_file.write(source)
                file_path = source_file.name

            result = subprocess.run(
                [resolved_node, "--check", file_path],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                return {
                    "syntax_valid": True,
                    "validator_available": True,
                    "error": None,
                }

            error = (result.stderr or result.stdout or "").strip()
            return {
                "syntax_valid": False,
                "validator_available": True,
                "error": (error or "JavaScript syntax check failed.")[:300],
            }

        except subprocess.TimeoutExpired:
            return {
                "syntax_valid": None,
                "validator_available": True,
                "error": "JavaScript syntax check timed out.",
            }
        except OSError as exc:
            return {
                "syntax_valid": None,
                "validator_available": False,
                "error": f"Could not run Node.js: {str(exc)[:200]}",
            }
        finally:
            if file_path:
                try:
                    Path(file_path).unlink(missing_ok=True)
                except OSError:
                    pass
