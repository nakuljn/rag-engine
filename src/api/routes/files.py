from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from api.api_constants import *
from models.api_models import ApiResponse, ApiResponseWithBody
from services.file_service import FileService

router = APIRouter()
file_service = FileService()

@router.post(FILES_BASE)
def upload_file(file: UploadFile = File(...)):
    result = file_service.upload_file(file)
    if result["success"]:
        return ApiResponseWithBody(
            status="SUCCESS",
            message="File uploaded successfully",
            body={"file_id": result["file_id"]}
        )
    else:
        return ApiResponseWithBody(
            status="FAILURE",
            message=result["error"],
            body={}
        )

@router.get(FILES_BASE)
def list_files():
    files = file_service.list_files()
    return ApiResponseWithBody(
        status="SUCCESS",
        message="Files retrieved successfully",
        body={"files": files}
    )

@router.get(FILES_BASE + "/{file_id}")
def get_file(file_id: str):
    if file_service.file_exists(file_id):
        return ApiResponse(status="SUCCESS", message=f"File '{file_id}' retrieved successfully")
    else:
        return ApiResponse(status="FAILURE", message="File not found")


@router.delete(FILES_BASE + "/{file_id}")
def delete_file(file_id: str):
    success = file_service.delete_file(file_id)
    if success:
        return ApiResponse(status="SUCCESS", message=f"File '{file_id}' deleted successfully")
    else:
        return ApiResponse(status="FAILURE", message="File not found or could not be deleted")