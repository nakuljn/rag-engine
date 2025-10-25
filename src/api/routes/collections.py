from fastapi import APIRouter, HTTPException
from typing import List
from ..api_constants import *

router = APIRouter()

@router.get(COLLECTIONS_BASE)
def get_collections():
    return {"collections": []}

@router.post(COLLECTIONS_BASE)
def create_collection():
    return {"message": "Collection created", "collection_id": "placeholder"}

@router.delete(COLLECTIONS_BASE + "/{collection_name}")
def delete_collection(collection_name: str):
    return {"message": f"Collection '{collection_name}' deleted"}

@router.post(COLLECTION_STATUS)
def get_collection_status():
    return {"status": "placeholder"}

@router.post("/{collection_name}" + LINK_CONTENT)
def link_content(collection_name: str):
    return {"message": f"Content linked to collection '{collection_name}'"}

@router.post("/{collection_name}" + UNLINK_CONTENT)
def unlink_content(collection_name: str):
    return {"message": f"Content unlinked from collection '{collection_name}'"}

@router.post("/{collection_name}" + QUERY_COLLECTION)
def query_collection(collection_name: str):
    return {"query_result": f"Placeholder query result for collection '{collection_name}'"}

@router.post("/{collection_name}" + BATCH_READ_FILES)
def batch_read_files(collection_name: str):
    return {"files_status": f"Placeholder batch read status for collection '{collection_name}'"}