import json
from uuid import uuid4

from fastapi.testclient import TestClient
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

from app.main import app
from app.retrieval import retrieve
from evaluation.judge import GroqJudge


QUESTIONS = [
    "What are the refund eligibility requirements?",
    "How do I reset my password?",
    "Can PC players play with Xbox players?",
]


def main():
    judge = GroqJudge()
    results = []

    with TestClient(app) as client:
        for question in QUESTIONS:
            response = client.post("/chat", json={
                "user_id": "deepeval-user",
                "thread_id": str(uuid4()),
                "message": question,
            })
            response.raise_for_status()
            answer = response.json()["answer"]

            # Fresh threads use the original question for retrieval.
            documents = retrieve(question)

            case = LLMTestCase(
                input=question,
                actual_output=answer,
                retrieval_context=[
                    doc["text"] for doc in documents
                ],
            )

            metrics = [
                FaithfulnessMetric(
                    model=judge,
                    threshold=0.8,
                    async_mode=False,
                ),
                AnswerRelevancyMetric(
                    model=judge,
                    threshold=0.8,
                    async_mode=False,
                ),
            ]

            record = {
                "question": question,
                "answer": answer,
                "metrics": {},
            }

            print(f"\nQUESTION: {question}")

            for metric in metrics:
                metric.measure(case)

                record["metrics"][metric.__name__] = {
                    "score": metric.score,
                    "passed": metric.is_successful(),
                    "reason": metric.reason,
                }

                print(
                    f"{metric.__name__}: {metric.score}"
                    f" | Passed: {metric.is_successful()}"
                )

            results.append(record)

    with open(
        "evaluation/results.json", "w", encoding="utf-8"
    ) as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print("\nSaved evaluation/results.json")

    failed = any(
        not metric_result["passed"]
        for record in results
        for metric_result in record["metrics"].values()
    )

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()