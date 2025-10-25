from fastapi import APIRouter, HTTPException
from typing import List
from api.api_constants import *
from models.api_models import CreateCollectionRequest, ApiResponse, LinkContentItem, LinkContentResponse
from services.collection_service import CollectionService

router = APIRouter()
collection_service = CollectionService()

@router.get(COLLECTIONS_BASE + "/{collection_name}")
def get_collection(collection_name: str):
    result = collection_service.get_collection(collection_name)
    if result["success"]:
        return ApiResponse(status="SUCCESS", message=f"Collection '{collection_name}' exists")
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


@router.post("/{collection_name}" + LINK_CONTENT)
def link_content(collection_name: str, files: List[LinkContentItem]):
    result = collection_service.link_content(collection_name, files)
    return result

@router.post("/{collection_name}" + UNLINK_CONTENT)
def unlink_content(collection_name: str, file_ids: List[str]):
    result = collection_service.unlink_content(collection_name, file_ids)
    return result

@router.post("/{collection_name}" + QUERY_COLLECTION)
def query_collection(collection_name: str):
    return {"query_result": f"Placeholder query result for collection '{collection_name}'"}

