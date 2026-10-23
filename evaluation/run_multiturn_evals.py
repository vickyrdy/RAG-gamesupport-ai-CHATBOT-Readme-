import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from deepeval.metrics import ConversationRelevancyMetric
from deepeval.test_case import ConversationalTestCase, LLMTestCase

from app.main import app
from evaluation.judge import GroqJudge


QUESTIONS = [
    "How do I reset my password?",
    "How long is that link valid?",
]

OUTPUT = Path(__file__).resolve().parent / "multiturn_results.json"


def main():
    turns = []
    thread_id = str(uuid4())

    with TestClient(app) as client:
        for question in QUESTIONS:
            response = client.post(
                "/chat",
                json={
                    "user_id": "multiturn-eval-user",
                    "thread_id": thread_id,
                    "message": question,
                },
            )
            response.raise_for_status()
            data = response.json()

            if data.get("blocked"):
                raise RuntimeError(
                    f"Normal support question was blocked: {question}"
                )

            answer = data["answer"]
            turns.append(
                LLMTestCase(
                    input=question,
                    actual_output=answer,
                )
            )

            print(f"\nUSER: {question}")
            print(f"ASSISTANT: {answer}")

    case = ConversationalTestCase(
        turns=turns,
        name="Password reset follow-up",
    )

    metric = ConversationRelevancyMetric(
        model=GroqJudge(),
        threshold=0.8,
        async_mode=False,
        window_size=3,
        include_reason=True,
    )
    metric.measure(case)

    passed = metric.is_successful()

    result = {
        "name": case.name,
        "thread_id": thread_id,
        "turns": [
            {
                "question": turn.input,
                "answer": turn.actual_output,
            }
            for turn in turns
        ],
        "metric": {
            "name": metric.__name__,
            "threshold": 0.8,
            "score": metric.score,
            "passed": passed,
            "reason": metric.reason,
        },
    }

    OUTPUT.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nConversation relevancy: {metric.score}")
    print(f"Passed: {passed}")
    print(f"Reason: {metric.reason}")
    print(f"Saved: {OUTPUT}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()