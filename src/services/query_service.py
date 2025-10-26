from typing import List, Dict, Any
from repositories.qdrant_repository import QdrantRepository
from utils.embedding_client import EmbeddingClient
from utils.llm_client import LlmClient
from models.api_models import QueryResponse, ChunkConfig
from core.reranker import reranker

class QueryService:
    def __init__(self):
        self.qdrant_repo = QdrantRepository()
        self.embedding_client = EmbeddingClient()
        self.llm_client = LlmClient()

    def _filter_relevant_results(self, results: List[Dict], threshold: float = 0.5) -> List[Dict]:
        return [result for result in results if result.get("score", 0) >= threshold]

    def _is_valid_text(self, text: str) -> bool:
        if not text or len(text.strip()) == 0:
            return False
        printable_chars = sum(1 for c in text if c.isprintable() or c.isspace())
        return (printable_chars / len(text)) > 0.8

    def _extract_relevant_chunks(self, results: List[Dict]) -> List[ChunkConfig]:
        if not results:
            return []

        chunks = []
        for result in results:
            payload = result.get("payload", {})
            text = payload.get("text", "")
            source = payload.get("document_id", "unknown")

            if text and self._is_valid_text(text):
                trimmed_text = text[:150] + "..." if len(text) > 150 else text
                chunks.append(ChunkConfig(source=source, text=trimmed_text))

        return chunks[:3]

    def _calculate_confidence(self, results: List[Dict]) -> float:
        if not results:
            return 0.0
        return max(result.get("score", 0) for result in results)

    def _create_query_response(self, results: List[Dict], query: str) -> QueryResponse:
        relevant_results = self._filter_relevant_results(results)

        if not relevant_results:
            return QueryResponse(
                answer="Context not found",
                confidence=0.0,
                missing_info="No relevant information found for the given query",
                is_relevant=False,
                chunks=[]
            )

        chunks = self._extract_relevant_chunks(relevant_results)

        if not chunks:
            return QueryResponse(
                answer="Error: Stored content is corrupted or unreadable",
                confidence=0.0,
                missing_info="Relink your files to fix corrupted content",
                is_relevant=False,
                chunks=[]
            )

        chunk_texts = [chunk.text for chunk in chunks]
        answer = self.llm_client.generate_answer(query, chunk_texts)
        confidence = self._calculate_confidence(relevant_results)

        return QueryResponse(
            answer=answer,
            confidence=confidence,
            missing_info="",
            is_relevant=True,
            chunks=chunks
        )

    def search(self, collection_name: str, query_text: str, limit: int = 5) -> QueryResponse:
        try:
            query_vector = self.embedding_client.generate_single_embedding(query_text)
            results = self.qdrant_repo.query_collection(collection_name, query_vector, limit)

            # Apply reranking if available and enabled
            if reranker.is_available() and results:
                results = reranker.rerank(query_text, results)

            return self._create_query_response(results, query_text)
        except Exception as e:
            return QueryResponse(
                answer="Context not found",
                confidence=0.0,
                missing_info=f"Failed to search collection: {str(e)}",
                is_relevant=False,
                chunks=[]
            )