from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
import os
from ..api_constants import *
from models.api_models import ApiResponse, ApiResponseWithBody

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post(FILES_BASE)
def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        return ApiResponseWithBody(
            status="SUCCESS",
            message="File uploaded successfully",
            body={"file_id": file_id}
        )
    except Exception:
        return ApiResponseWithBody(
            status="FAILURE",
            message="File upload failed",
            body={}
        )

@router.get(FILES_BASE)
def list_files():
    return ApiResponse(status="SUCCESS", message="Files retrieved successfully")

@router.get(FILES_BASE + "/{file_id}")
def get_file(file_id: str):
    return ApiResponse(status="SUCCESS", message=f"File '{file_id}' retrieved successfully")

@router.put(FILES_BASE + "/{file_id}")
def update_file(file_id: str):
    raise HTTPException(status_code=503, detail="Not implemented")

@router.delete(FILES_BASE + "/{file_id}")
def delete_file(file_id: str):
    return ApiResponse(status="SUCCESS", message=f"File '{file_id}' deleted successfully")