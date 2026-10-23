from pathlib import Path
from qdrant_client import QdrantClient, models

ROOT = Path(__file__).resolve().parents[1]
MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def retrieve(question: str, limit: int = 5):
    client = QdrantClient(path=str(ROOT / ".qdrant"))
    try:
        hits = client.query_points(
            collection_name="game_support",
            query=models.Document(text=question, model=MODEL),
            limit=limit,
            with_payload=True,
        ).points

        return [
            {
                "text": hit.payload["text"],
                "source": hit.payload["source"],
                "score": hit.score,
            }
            for hit in hits
        ]
    finally:
        client.close()


if __name__ == "__main__":
    question = input("Ask a support question: ")
    for result in retrieve(question):
        print(f"\nSource: {result['source']}")
        print(result["text"])