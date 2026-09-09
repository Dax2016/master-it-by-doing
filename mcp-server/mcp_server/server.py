from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Master It By Doing")


@mcp.tool()
def create_learning_goal(skill: str, learner_level: str = "beginner") -> dict:
    """
    Create a practical learning goal for the learner.

    Args:
        skill: The skill the learner wants to learn.
        learner_level: The learner's current level.
    """
    return {
        "status": "created",
        "skill": skill,
        "learner_level": learner_level,
        "message": (
            f"Learning goal created: learn {skill} "
            f"at {learner_level} level."
        ),
        "next_action": "Create a practical learning mission.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")