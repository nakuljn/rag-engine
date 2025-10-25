from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition
from typing import List, Dict, Any, Optional
import uuid
from config import Config

class QdrantRepository:
    def __init__(self):
        self.client = QdrantClient(
            host=Config.database.QDRANT_HOST,
            port=Config.database.QDRANT_PORT,
            timeout=Config.database.QDRANT_TIMEOUT
        )

    def collection_exists(self, collection_name: str) -> bool:
        try:
            return self.client.collection_exists(collection_name)
        except Exception:
            return False

    def create_collection(self, collection_name: str) -> bool:
        try:
            if self.collection_exists(collection_name):
                return False

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=Config.embedding.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            return True
        except Exception:
            return False

    def delete_collection(self, collection_name: str) -> bool:
        try:
            self.client.delete_collection(collection_name)
            return True
        except Exception:
            return False

    def list_collections(self) -> List[str]:
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception:
            return []


    def link_content(self, collection_name: str, documents: List[Dict[str, Any]]) -> bool:
        try:
            points = []
            for doc in documents:
                text = doc.get("text", "")
                vector = doc.get("vector", [])

                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "document_id": doc.get("document_id"),
                        "text": text,
                        "source": doc.get("source", ""),
                        "metadata": doc.get("metadata", {})
                    }
                )
                points.append(point)

            self.client.upsert(collection_name=collection_name, points=points)
            return True
        except Exception:
            return False

    def unlink_content(self, collection_name: str, document_ids: List[str]) -> bool:
        try:
            for doc_id in document_ids:
                self.client.delete(
                    collection_name=collection_name,
                    points_selector=Filter(
                        must=[FieldCondition(key="document_id", match={"value": doc_id})]
                    )
                )
            return True
        except Exception:
            return False

    def query_collection(self, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )

            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in results
            ]
        except Exception:
            return []

    def batch_read_files(self, collection_name: str, document_ids: List[str]) -> Dict[str, Any]:
        try:
            status = {}
            for doc_id in document_ids:
                results = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=Filter(
                        must=[FieldCondition(key="document_id", match={"value": doc_id})]
                    ),
                    limit=1
                )
                status[doc_id] = "indexed" if results[0] else "not_found"
            return status
        except Exception:
            return {doc_id: "error" for doc_id in document_ids}