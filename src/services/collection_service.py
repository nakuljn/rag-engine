from typing import List, Dict, Any, Optional
from ..repositories.qdrant_repository import QdrantRepository
from ..utils.embedding_client import EmbeddingClient
from .file_service import FileService

class CollectionService:
    def __init__(self):
        self.qdrant_repo = QdrantRepository()
        self.embedding_client = EmbeddingClient()
        self.file_service = FileService()

    def create_collection(self, name: str, rag_config: Optional[Dict] = None, indexing_config: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            success = self.qdrant_repo.create_collection(name)
            if success:
                return {
                    "success": True,
                    "message": "Collection created successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create collection, already exists"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create collection: {str(e)}"
            }

    def delete_collection(self, name: str) -> Dict[str, Any]:
        try:
            success = self.qdrant_repo.delete_collection(name)
            if success:
                return {
                    "success": True,
                    "message": f"Collection '{name}' deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to delete collection '{name}'"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete collection: {str(e)}"
            }

    def list_collections(self) -> Dict[str, Any]:
        try:
            collections = self.qdrant_repo.list_collections()
            return {
                "success": True,
                "collections": collections
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to list collections: {str(e)}"
            }

    def get_collection_status(self, name: str) -> Dict[str, Any]:
        try:
            status = self.qdrant_repo.get_collection_status(name)
            return {
                "success": True,
                "status": status
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get collection status: {str(e)}"
            }

    def _validate_file_exists(self, file_id: str) -> Dict[str, Any]:
        if not self.file_service.file_exists(file_id):
            return {
                "success": False,
                "message": "File not found"
            }
        return {"success": True}

    def _validate_collection_exists(self, collection_name: str) -> Dict[str, Any]:
        if not self.qdrant_repo.collection_exists(collection_name):
            return {
                "success": False,
                "message": f"Collection '{collection_name}' does not exist"
            }
        return {"success": True}

    def _get_file_content(self, file_id: str) -> Dict[str, Any]:
        file_content = self.file_service.get_file_content(file_id)
        if not file_content:
            return {
                "success": False,
                "message": "Could not read file content"
            }
        return {
            "success": True,
            "content": file_content
        }

    def _generate_embedding_and_document(self, file_id: str, file_content: str, file_type: str) -> Dict[str, Any]:
        try:
            embedding = self.embedding_client.generate_single_embedding(file_content)
            documents = [{
                "document_id": file_id,
                "text": file_content,
                "source": file_type,
                "metadata": {"file_type": file_type},
                "vector": embedding
            }]
            return {
                "success": True,
                "documents": documents
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to generate embedding: {str(e)}"
            }

    def link_content(self, collection_name: str, file_id: str, file_type: str) -> Dict[str, Any]:
        file_validation = self._validate_file_exists(file_id)
        if not file_validation["success"]:
            return file_validation

        collection_validation = self._validate_collection_exists(collection_name)
        if not collection_validation["success"]:
            return collection_validation

        content_result = self._get_file_content(file_id)
        if not content_result["success"]:
            return content_result

        embedding_result = self._generate_embedding_and_document(file_id, content_result["content"], file_type)
        if not embedding_result["success"]:
            return embedding_result

        try:
            success = self.qdrant_repo.link_content(collection_name, embedding_result["documents"])
            if success:
                return {
                    "success": True,
                    "message": f"Content linked to collection '{collection_name}'"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to link content to collection"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to link content: {str(e)}"
            }

    def unlink_content(self, collection_name: str, document_ids: List[str]) -> Dict[str, Any]:
        try:
            success = self.qdrant_repo.unlink_content(collection_name, document_ids)
            if success:
                return {
                    "success": True,
                    "message": f"Content unlinked from collection '{collection_name}'"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to unlink content from collection"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to unlink content: {str(e)}"
            }

    def query_collection(self, collection_name: str, query_text: str, limit: int = 5) -> Dict[str, Any]:
        try:
            query_vector = self.embedding_client.generate_single_embedding(query_text)
            results = self.qdrant_repo.query_collection(collection_name, query_vector, limit)
            return {
                "success": True,
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to query collection: {str(e)}"
            }

    def batch_read_files(self, collection_name: str, document_ids: List[str]) -> Dict[str, Any]:
        try:
            status = self.qdrant_repo.batch_read_files(collection_name, document_ids)
            return {
                "success": True,
                "files_status": status
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to read files status: {str(e)}"
            }