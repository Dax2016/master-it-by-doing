import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "mcp-server" / "mcp_server" / "server.py"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SPEC = importlib.util.spec_from_file_location(
    "master_it_by_doing_mcp_server",
    SERVER_PATH,
)
assert SPEC is not None
assert SPEC.loader is not None

MCP_SERVER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MCP_SERVER
SPEC.loader.exec_module(MCP_SERVER)


@pytest.mark.parametrize(
    "mission_input",
    [
        "build-number-guessing-game",
        "Build a Number Guessing Game",
    ],
)
def test_resolve_number_guessing_game_to_canonical_mission(
    mission_input: str,
) -> None:
    resolved = MCP_SERVER.resolve_mission(
        skill="Python",
        mission=mission_input,
    )

    assert resolved["id"] == "build-number-guessing-game"
    assert resolved["title"] == "Build a Number Guessing Game"
    assert len(resolved["criteria"]) == 4
    assert {
        criterion["id"] for criterion in resolved["criteria"]
    } == {
        "random_number",
        "user_input",
        "feedback",
        "multiple_attempts",
    }
