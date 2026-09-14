from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable


class ParallelEvaluator:
    """
    Runs independent evaluation aspects in parallel.

    Each evaluator receives the same mission and learner attempt,
    but focuses on a different aspect of the learner's work.
    """

    def __init__(self, evaluators: dict[str, Callable]):
        self.evaluators = evaluators

    def evaluate(
        self,
        mission: dict,
        attempt: dict,
    ) -> dict[str, dict]:
        """
        Execute all evaluation aspects concurrently.

        Returns:
            A dictionary mapping each aspect name to its evaluation result.
        """
        results: dict[str, dict] = {}

        with ThreadPoolExecutor(
            max_workers=len(self.evaluators)
        ) as executor:

            futures = {
                executor.submit(
                    evaluator,
                    mission,
                    attempt,
                ): name
                for name, evaluator in self.evaluators.items()
            }

            for future in as_completed(futures):
                name = futures[future]

                try:
                    results[name] = future.result()
                except Exception as exc:
                    results[name] = {
                        "status": "error",
                        "error": str(exc),
                    }

        return results


class EvaluationAggregator:
    """
    Combines independent evaluation results into one structured result.

    This layer aggregates evidence only.
    It does not determine the authoritative pass/fail decision.
    Ground Truth remains responsible for that decision.
    """

    def aggregate(self, results: dict[str, dict]) -> dict:
        successful = {
            name: result
            for name, result in results.items()
            if result.get("status") != "error"
        }

        failed = {
            name: result
            for name, result in results.items()
            if result.get("status") == "error"
        }

        return {
            "aspects_evaluated": list(results.keys()),
            "successful_aspects": list(successful.keys()),
            "failed_aspects": list(failed.keys()),
            "results": results,
        }

