from pathlib import Path
from qdrant_client import QdrantClient, models
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parents[1]
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION = "game_support"


def main():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700, chunk_overlap=100
    )
    payloads = []

    for file in sorted((ROOT / "data" / "docs").glob("*.md")):
        text = file.read_text(encoding="utf-8-sig")
        for chunk in splitter.split_text(text):
            payloads.append({"text": chunk, "source": file.name})

    if not payloads:
        raise RuntimeError("No documents found in data/docs.")

    client = QdrantClient(path=str(ROOT / ".qdrant"))
    try:
        if client.collection_exists(COLLECTION):
            client.delete_collection(COLLECTION)

        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=client.get_embedding_size(MODEL),
                distance=models.Distance.COSINE,
            ),
        )

        client.upload_collection(
            collection_name=COLLECTION,
            vectors=[
                models.Document(text=p["text"], model=MODEL)
                for p in payloads
            ],
            payload=payloads,
            ids=list(range(len(payloads))),
        )
        print(f"Indexed {len(payloads)} chunks successfully.")
    finally:
        client.close()


if __name__ == "__main__":
    main()