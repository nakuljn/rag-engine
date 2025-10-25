from fastapi import APIRouter, HTTPException
from typing import List
from ..api_constants import *
from models.api_models import FileUploadRequest, FileUpdateRequest, ApiResponse

router = APIRouter()

@router.post(FILES_BASE)
def upload_file(request: FileUploadRequest):
    return ApiResponse(status="SUCCESS", message="File uploaded successfully")

@router.get(FILES_BASE)
def list_files():
    return ApiResponse(status="SUCCESS", message="Files retrieved successfully")

@router.get(FILES_BASE + "/{file_id}")
def get_file(file_id: str):
    return ApiResponse(status="SUCCESS", message=f"File '{file_id}' retrieved successfully")

@router.put(FILES_BASE + "/{file_id}")
def update_file(file_id: str, request: FileUpdateRequest):
    raise HTTPException(status_code=503, detail="Not implemented")

@router.delete(FILES_BASE + "/{file_id}")
def delete_file(file_id: str):
    return ApiResponse(status="SUCCESS", message=f"File '{file_id}' deleted successfully")