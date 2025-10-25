from typing import List, Dict, Any, Optional
from datetime import datetime
from repositories.qdrant_repository import QdrantRepository
from utils.embedding_client import EmbeddingClient
from services.file_service import FileService
from services.query_service import QueryService
from models.api_models import LinkContentItem, LinkContentResponse, ApiResponse, ApiResponseWithBody, QueryResponse, UnlinkContentResponse

class CollectionService:
    def __init__(self):
        self.qdrant_repo = QdrantRepository()
        self.embedding_client = EmbeddingClient()
        self.file_service = FileService()
        self.query_service = QueryService()

    def create_collection(self, name: str, rag_config: Optional[Dict] = None, indexing_config: Optional[Dict] = None) -> ApiResponse:
        try:
            success = self.qdrant_repo.create_collection(name)
            if success:
                return ApiResponse(status="SUCCESS", message="Collection created successfully")
            else:
                return ApiResponse(status="FAILURE", message="Failed to create collection, already exists")
        except Exception as e:
            return ApiResponse(status="FAILURE", message=f"Failed to create collection: {str(e)}")

    def delete_collection(self, name: str) -> ApiResponse:
        try:
            success = self.qdrant_repo.delete_collection(name)
            if success:
                return ApiResponse(status="SUCCESS", message=f"Collection '{name}' deleted successfully")
            else:
                return ApiResponse(status="FAILURE", message=f"Failed to delete collection '{name}'")
        except Exception as e:
            return ApiResponse(status="FAILURE", message=f"Failed to delete collection: {str(e)}")

    def list_collections(self) -> ApiResponseWithBody:
        try:
            collections = self.qdrant_repo.list_collections()
            return ApiResponseWithBody(status="SUCCESS", message="Collections retrieved successfully", body={"collections": collections})
        except Exception as e:
            return ApiResponseWithBody(status="FAILURE", message=f"Failed to list collections: {str(e)}", body={})

    def get_collection(self, name: str) -> ApiResponse:
        try:
            exists = self.qdrant_repo.collection_exists(name)
            if exists:
                return ApiResponse(status="SUCCESS", message=f"Collection '{name}' exists")
            else:
                return ApiResponse(status="FAILURE", message=f"Collection '{name}' not found")
        except Exception as e:
            return ApiResponse(status="FAILURE", message=f"Failed to check collection: {str(e)}")

    def _validate_file_exists(self, file_id: str) -> bool:
        return self.file_service.file_exists(file_id)

    def _validate_collection_exists(self, collection_name: str) -> bool:
        return self.qdrant_repo.collection_exists(collection_name)

    def _get_file_content(self, file_id: str) -> Optional[str]:
        return self.file_service.get_file_content(file_id)

    def _generate_embedding_and_document(self, file_id: str, file_content: str, file_type: str) -> Optional[List[Dict[str, Any]]]:
        try:
            embedding = self.embedding_client.generate_single_embedding(file_content)
            documents = [{
                "document_id": file_id,
                "text": file_content,
                "source": file_type,
                "metadata": {"file_type": file_type},
                "vector": embedding
            }]
            return documents
        except Exception:
            return None

    def _check_file_already_linked(self, collection_name: str, file_id: str) -> bool:
        try:
            status = self.qdrant_repo.batch_read_files(collection_name, [file_id])
            return status.get(file_id) == "indexed"
        except Exception:
            return False

    def _create_link_error_response(self, file_item: LinkContentItem, status_code: int, message: str) -> LinkContentResponse:
        return LinkContentResponse(
            name=file_item.name,
            id=file_item.file_id,
            field=file_item.type,
            created_at=None,
            indexing_status="INDEXING_FAILED",
            status_code=status_code,
            message=message
        )

    def _create_link_success_response(self, file_item: LinkContentItem) -> LinkContentResponse:
        return LinkContentResponse(
            name=file_item.name,
            id=file_item.file_id,
            field=file_item.type,
            created_at=datetime.now().isoformat(),
            indexing_status="INDEXING_SUCCESS",
            status_code=200,
            message="Successfully linked to collection"
        )

    def _create_unlink_response(self, file_id: str, status_code: int, message: str) -> UnlinkContentResponse:
        return UnlinkContentResponse(
            file_id=file_id,
            status_code=status_code,
            message=message
        )


    def link_content(self, collection_name: str, files: List[LinkContentItem]) -> List[LinkContentResponse]:
        responses = []

        if not self._validate_collection_exists(collection_name):
            for file_item in files:
                responses.append(self._create_link_error_response(
                    file_item, 404, f"Collection '{collection_name}' does not exist"
                ))
            return responses

        for file_item in files:
            try:
                if not self._validate_file_exists(file_item.file_id):
                    responses.append(self._create_link_error_response(file_item, 404, "File not found"))
                    continue

                if self._check_file_already_linked(collection_name, file_item.file_id):
                    responses.append(self._create_link_error_response(file_item, 409, "File already linked, unlink first"))
                    continue

                file_content = self._get_file_content(file_item.file_id)
                if not file_content:
                    responses.append(self._create_link_error_response(file_item, 500, "Could not read file content"))
                    continue

                documents = self._generate_embedding_and_document(
                    file_item.file_id, file_content, file_item.type
                )
                if not documents:
                    responses.append(self._create_link_error_response(file_item, 500, "Failed to generate embedding"))
                    continue

                success = self.qdrant_repo.link_content(collection_name, documents)
                if success:
                    responses.append(self._create_link_success_response(file_item))
                else:
                    responses.append(self._create_link_error_response(file_item, 500, "Failed to link content to collection"))

            except Exception as e:
                responses.append(self._create_link_error_response(file_item, 500, f"Internal error: {str(e)}"))

        return responses

    def unlink_content(self, collection_name: str, file_ids: List[str]) -> List[UnlinkContentResponse]:
        responses = []

        if not self._validate_collection_exists(collection_name):
            for file_id in file_ids:
                responses.append(self._create_unlink_response(file_id, 404, f"Collection '{collection_name}' does not exist"))
            return responses

        for file_id in file_ids:
            try:
                if not self._check_file_already_linked(collection_name, file_id):
                    responses.append(self._create_unlink_response(file_id, 404, "File not found in collection"))
                    continue

                success = self.qdrant_repo.unlink_content(collection_name, [file_id])
                if success:
                    responses.append(self._create_unlink_response(file_id, 200, "Successfully unlinked from collection"))
                else:
                    responses.append(self._create_unlink_response(file_id, 500, "Failed to unlink content from collection"))

            except Exception as e:
                responses.append(self._create_unlink_response(file_id, 500, f"Internal error: {str(e)}"))

        return responses

    def query_collection(self, collection_name: str, query_text: str, limit: int = 5) -> QueryResponse:
        if not self._validate_collection_exists(collection_name):
            return QueryResponse(
                answer="Context not found",
                confidence=0.0,
                missing_info=f"Collection '{collection_name}' does not exist"
            )

        if not query_text.strip():
            return QueryResponse(
                answer="Context not found",
                confidence=0.0,
                missing_info="Empty query provided"
            )

        return self.query_service.search(collection_name, query_text, limit)

