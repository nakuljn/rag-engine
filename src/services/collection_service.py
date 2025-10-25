from typing import List, Dict, Any, Optional
from datetime import datetime
from repositories.qdrant_repository import QdrantRepository
from utils.embedding_client import EmbeddingClient
from services.file_service import FileService
from models.api_models import LinkContentItem, LinkContentResponse

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

    def get_collection(self, name: str) -> Dict[str, Any]:
        try:
            exists = self.qdrant_repo.collection_exists(name)
            if exists:
                return {
                    "success": True,
                    "message": f"Collection '{name}' exists"
                }
            else:
                return {
                    "success": False,
                    "message": f"Collection '{name}' not found"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to check collection: {str(e)}"
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

    def _check_file_already_linked(self, collection_name: str, file_id: str) -> bool:
        """Check if file is already linked to collection"""
        try:
            # Use existing batch_read_files method to check if document exists
            status = self.qdrant_repo.batch_read_files(collection_name, [file_id])
            return status.get(file_id) == "indexed"
        except Exception:
            return False

    def link_content(self, collection_name: str, files: List[LinkContentItem]) -> List[LinkContentResponse]:
        responses = []

        # First check if collection exists - if not, return 404 for all files
        collection_validation = self._validate_collection_exists(collection_name)
        if not collection_validation["success"]:
            for file_item in files:
                responses.append(LinkContentResponse(
                    name=file_item.name,
                    id=file_item.id,
                    field=file_item.field,
                    created_at=None,
                    indexing_status="INDEXING_FAILED",
                    status_code=404,
                    message=collection_validation["message"]
                ))
            return responses

        # Process each file individually
        for file_item in files:
            try:
                # Check if file exists
                file_validation = self._validate_file_exists(file_item.id)
                if not file_validation["success"]:
                    responses.append(LinkContentResponse(
                        name=file_item.name,
                        id=file_item.id,
                        field=file_item.field,
                        created_at=None,
                        indexing_status="INDEXING_FAILED",
                        status_code=404,
                        message="File not found"
                    ))
                    continue

                # Check if file is already linked
                if self._check_file_already_linked(collection_name, file_item.id):
                    responses.append(LinkContentResponse(
                        name=file_item.name,
                        id=file_item.id,
                        field=file_item.field,
                        created_at=None,
                        indexing_status="INDEXING_FAILED",
                        status_code=409,
                        message="File already linked, unlink first"
                    ))
                    continue

                # Get file content
                content_result = self._get_file_content(file_item.id)
                if not content_result["success"]:
                    responses.append(LinkContentResponse(
                        name=file_item.name,
                        id=file_item.id,
                        field=file_item.field,
                        created_at=None,
                        indexing_status="INDEXING_FAILED",
                        status_code=500,
                        message="Could not read file content"
                    ))
                    continue

                # Generate embedding and link content
                embedding_result = self._generate_embedding_and_document(
                    file_item.id, content_result["content"], file_item.field
                )
                if not embedding_result["success"]:
                    responses.append(LinkContentResponse(
                        name=file_item.name,
                        id=file_item.id,
                        field=file_item.field,
                        created_at=None,
                        indexing_status="INDEXING_FAILED",
                        status_code=500,
                        message=embedding_result["message"]
                    ))
                    continue

                # Link to Qdrant (synchronous operation)
                success = self.qdrant_repo.link_content(collection_name, embedding_result["documents"])
                if success:
                    responses.append(LinkContentResponse(
                        name=file_item.name,
                        id=file_item.id,
                        field=file_item.field,
                        created_at=datetime.now().isoformat(),
                        indexing_status="INDEXING_SUCCESS",
                        status_code=200,
                        message="Successfully linked to collection"
                    ))
                else:
                    responses.append(LinkContentResponse(
                        name=file_item.name,
                        id=file_item.id,
                        field=file_item.field,
                        created_at=None,
                        indexing_status="INDEXING_FAILED",
                        status_code=500,
                        message="Failed to link content to collection"
                    ))

            except Exception as e:
                responses.append(LinkContentResponse(
                    name=file_item.name,
                    id=file_item.id,
                    field=file_item.field,
                    created_at=None,
                    indexing_status="INDEXING_FAILED",
                    status_code=500,
                    message=f"Internal error: {str(e)}"
                ))

        return responses

    def unlink_content(self, collection_name: str, file_ids: List[str]) -> List[Dict[str, Any]]:
        responses = []

        # First check if collection exists - if not, return 404 for all files
        collection_validation = self._validate_collection_exists(collection_name)
        if not collection_validation["success"]:
            for file_id in file_ids:
                responses.append({
                    "file_id": file_id,
                    "status_code": 404,
                    "message": collection_validation["message"]
                })
            return responses

        # Process each file individually
        for file_id in file_ids:
            try:
                # Check if file exists in collection
                if not self._check_file_already_linked(collection_name, file_id):
                    responses.append({
                        "file_id": file_id,
                        "status_code": 404,
                        "message": "File not found in collection"
                    })
                    continue

                # Unlink from Qdrant
                success = self.qdrant_repo.unlink_content(collection_name, [file_id])
                if success:
                    responses.append({
                        "file_id": file_id,
                        "status_code": 200,
                        "message": "Successfully unlinked from collection"
                    })
                else:
                    responses.append({
                        "file_id": file_id,
                        "status_code": 500,
                        "message": "Failed to unlink content from collection"
                    })

            except Exception as e:
                responses.append({
                    "file_id": file_id,
                    "status_code": 500,
                    "message": f"Internal error: {str(e)}"
                })

        return responses

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

