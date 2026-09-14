from services.orchestration.parallel_evaluator import ParallelEvaluator


def code_evaluator(mission, attempt):
    return {
        "aspect": "code",
        "result": "Code structure reviewed",
    }


def logic_evaluator(mission, attempt):
    return {
        "aspect": "logic",
        "result": "Logic reviewed",
    }


def skill_evaluator(mission, attempt):
    return {
        "aspect": "skill",
        "result": "Skill application reviewed",
    }


def test_parallel_evaluation():
    evaluator = ParallelEvaluator(
        {
            "code": code_evaluator,
            "logic": logic_evaluator,
            "skill": skill_evaluator,
        }
    )

    results = evaluator.evaluate(
        mission={"title": "Build a Number Guessing Game"},
        attempt={"code": "print('hello')"},
    )

    assert set(results.keys()) == {
        "code",
        "logic",
        "skill",
    }

    assert results["code"]["aspect"] == "code"
    assert results["logic"]["aspect"] == "logic"
    assert results["skill"]["aspect"] == "skill"