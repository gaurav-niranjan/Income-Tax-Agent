"""Dense retrieval: embed the query, find the nearest chunk vectors in Chroma."""

from langchain_chroma import Chroma


class DenseRetriever:
    def __init__(self, store: Chroma):
        self.store = store

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        """Top-k (chunk_id, score), best first. Higher score = more similar."""
        results = self.store.similarity_search_with_score(query, k=k)
        # Chroma returns a distance (lower is closer). Negate it so all retrievers agree.
        return [(doc.metadata["chunk_id"], -distance) for doc, distance in results]
