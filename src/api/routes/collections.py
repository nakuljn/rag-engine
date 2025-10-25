from fastapi import APIRouter, HTTPException
from typing import List
from ..api_constants import *
from models.api_models import CreateCollectionRequest, ApiResponse
from services.collection_service import CollectionService

router = APIRouter()
collection_service = CollectionService()

@router.get(COLLECTIONS_BASE)
def get_collections():
    result = collection_service.list_collections()
    if result["success"]:
        return ApiResponse(status="SUCCESS", message="Collections retrieved successfully")
    else:
        return ApiResponse(status="FAILURE", message=result["message"])

@router.post(COLLECTIONS_BASE)
def create_collection(request: CreateCollectionRequest):
    result = collection_service.create_collection(
        request.name,
        request.rag_config.dict() if request.rag_config else None,
        request.indexing_config.dict() if request.indexing_config else None
    )
    if result["success"]:
        return ApiResponse(status="SUCCESS", message=result["message"])
    else:
        return ApiResponse(status="FAILURE", message=result["message"])

@router.delete(COLLECTIONS_BASE + "/{collection_name}")
def delete_collection(collection_name: str):
    result = collection_service.delete_collection(collection_name)
    if result["success"]:
        return ApiResponse(status="SUCCESS", message=result["message"])
    else:
        return ApiResponse(status="FAILURE", message=result["message"])

@router.post(COLLECTION_STATUS)
def get_collection_status():
    return ApiResponse(status="SUCCESS", message="Collection status retrieved")

@router.post("/{collection_name}" + LINK_CONTENT)
def link_content(collection_name: str, file_id: str, file_type: str):
    result = collection_service.link_content(collection_name, file_id, file_type)
    if result["success"]:
        return ApiResponse(status="SUCCESS", message=result["message"])
    else:
        return ApiResponse(status="FAILURE", message=result["message"])

@router.post("/{collection_name}" + UNLINK_CONTENT)
def unlink_content(collection_name: str):
    return {"message": f"Content unlinked from collection '{collection_name}'"}

@router.post("/{collection_name}" + QUERY_COLLECTION)
def query_collection(collection_name: str):
    return {"query_result": f"Placeholder query result for collection '{collection_name}'"}

@router.post("/{collection_name}" + BATCH_READ_FILES)
def batch_read_files(collection_name: str):
    return {"files_status": f"Placeholder batch read status for collection '{collection_name}'"}