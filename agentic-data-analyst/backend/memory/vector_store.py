"""ChromaDB-based vector store for agent memory and context retrieval."""
import logging
from typing import Optional

import chromadb
from chromadb.config import Settings

from config import MEMORY_DIR

logger = logging.getLogger(__name__)

_client: Optional[chromadb.ClientAPI] = None
_collection = None

COLLECTION_NAME = "analysis_memory"


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.Client(Settings(
            persist_directory=str(MEMORY_DIR),
            anonymized_telemetry=False,
        ))
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def store_analysis(question: str, summary: str, metadata: Optional[dict] = None):
    """Store an analysis result for future retrieval."""
    coll = get_collection()
    doc_id = f"analysis_{coll.count()}"
    meta = metadata or {}
    meta["question"] = question
    coll.add(
        documents=[summary],
        metadatas=[meta],
        ids=[doc_id],
    )
    logger.info("Stored analysis memory: %s", doc_id)


def retrieve_similar(query: str, n_results: int = 3) -> list[dict]:
    """Retrieve similar past analyses."""
    coll = get_collection()
    if coll.count() == 0:
        return []
    results = coll.query(query_texts=[query], n_results=min(n_results, coll.count()))
    out = []
    for i, doc in enumerate(results["documents"][0]):
        out.append({
            "document": doc,
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else None,
        })
    return out
