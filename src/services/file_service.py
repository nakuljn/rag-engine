from fastapi import UploadFile
import os
import uuid
from typing import Optional, Dict, Any

class FileService:
    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self, file: UploadFile) -> Dict[str, Any]:
        try:
            file_id = str(uuid.uuid4())
            file_path = os.path.join(self.upload_dir, f"{file_id}_{file.filename}")

            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)

            return {
                "success": True,
                "file_id": file_id,
                "file_path": file_path,
                "original_name": file.filename
            }
        except Exception:
            return {
                "success": False,
                "error": "File upload failed"
            }

    def file_exists(self, file_id: str) -> bool:
        files = os.listdir(self.upload_dir)
        for file in files:
            if file.startswith(f"{file_id}_"):
                return True
        return False

    def get_file_path(self, file_id: str) -> Optional[str]:
        files = os.listdir(self.upload_dir)
        for file in files:
            if file.startswith(f"{file_id}_"):
                return os.path.join(self.upload_dir, file)
        return None

    def get_file_content(self, file_id: str) -> Optional[str]:
        file_path = self.get_file_path(file_id)
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                with open(file_path, "rb") as f:
                    return f.read().decode("utf-8", errors="ignore")
        return None

    def delete_file(self, file_id: str) -> bool:
        file_path = self.get_file_path(file_id)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False