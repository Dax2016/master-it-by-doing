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
import time


def slow_evaluator(mission, attempt):
    time.sleep(0.25)
    return {"status": "ok"}


def test_parallel_evaluation_runs_concurrently():
    evaluator = ParallelEvaluator(
        {
            "one": slow_evaluator,
            "two": slow_evaluator,
            "three": slow_evaluator,
        }
    )

    start = time.perf_counter()

    results = evaluator.evaluate(
        mission={"title": "Concurrency Test"},
        attempt={"answer": "test"},
    )

    elapsed = time.perf_counter() - start

    assert set(results.keys()) == {"one", "two", "three"}

    # Sequential execution would take ~0.75s.
    # Parallel execution should be substantially faster.
    assert elapsed < 0.60


def failing_evaluator(mission, attempt):
    raise RuntimeError("Evaluator failed intentionally")


def test_parallel_evaluation_isolates_evaluator_failure():
    evaluator = ParallelEvaluator(
        {
            "code": code_evaluator,
            "failing": failing_evaluator,
            "skill": skill_evaluator,
        }
    )

    results = evaluator.evaluate(
        mission={"title": "Failure Isolation Test"},
        attempt={"code": "print('test')"},
    )

    # The successful evaluators must still complete.
    assert results["code"]["aspect"] == "code"
    assert results["skill"]["aspect"] == "skill"

    # The failed evaluator must be represented as structured error evidence.
    assert results["failing"]["status"] == "error"
    assert "Evaluator failed intentionally" in results["failing"]["error"]


from services.orchestration.parallel_evaluator import EvaluationAggregator


def test_evaluation_aggregator_separates_success_and_failure():
    aggregator = EvaluationAggregator()

    results = {
        "code": {
            "aspect": "code",
            "result": "Code reviewed",
        },
        "logic": {
            "aspect": "logic",
            "result": "Logic reviewed",
        },
        "broken": {
            "status": "error",
            "error": "Evaluator unavailable",
        },
    }

    aggregated = aggregator.aggregate(results)

    assert set(aggregated["aspects_evaluated"]) == {
        "code",
        "logic",
        "broken",
    }

    assert set(aggregated["successful_aspects"]) == {
        "code",
        "logic",
    }

    assert aggregated["failed_aspects"] == ["broken"]

    assert aggregated["results"] == results
