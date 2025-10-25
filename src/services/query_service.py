from typing import List, Dict, Any
from repositories.qdrant_repository import QdrantRepository
from utils.embedding_client import EmbeddingClient
from models.api_models import QueryResponse

class QueryService:
    def __init__(self):
        self.qdrant_repo = QdrantRepository()
        self.embedding_client = EmbeddingClient()

    def _filter_relevant_results(self, results: List[Dict], threshold: float = 0.5) -> List[Dict]:
        return [result for result in results if result.get("score", 0) >= threshold]

    def _extract_relevant_content(self, results: List[Dict]) -> str:
        if not results:
            return ""

        content_parts = []
        for result in results:
            text = result.get("payload", {}).get("text", "")
            if text:
                content_parts.append(text)

        return " ".join(content_parts[:3])

    def _calculate_confidence(self, results: List[Dict]) -> float:
        if not results:
            return 0.0
        return max(result.get("score", 0) for result in results)

    def _create_query_response(self, results: List[Dict]) -> QueryResponse:
        relevant_results = self._filter_relevant_results(results)

        if not relevant_results:
            return QueryResponse(
                answer="Context not found",
                confidence=0.0,
                missing_info="No relevant information found for the given query"
            )

        content = self._extract_relevant_content(relevant_results)
        confidence = self._calculate_confidence(relevant_results)

        return QueryResponse(
            answer=content,
            confidence=confidence,
            missing_info=""
        )

    def search(self, collection_name: str, query_text: str, limit: int = 5) -> QueryResponse:
        try:
            query_vector = self.embedding_client.generate_single_embedding(query_text)
            results = self.qdrant_repo.query_collection(collection_name, query_vector, limit)
            return self._create_query_response(results)
        except Exception as e:
            return QueryResponse(
                answer="Context not found",
                confidence=0.0,
                missing_info=f"Failed to search collection: {str(e)}"
            )