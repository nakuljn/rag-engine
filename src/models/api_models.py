from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class RagConfig(BaseModel):
    name: str
    version: str

class IndexingConfig(BaseModel):
    name: str
    version: str

class CreateCollectionRequest(BaseModel):
    name: str
    rag_config: Optional[RagConfig] = None
    indexing_config: Optional[IndexingConfig] = None

class ApiResponse(BaseModel):
    status: str
    message: str

class ApiResponseWithBody(BaseModel):
    status: str
    message: str
    body: Dict[str, Any]

class LinkContentItem(BaseModel):
    name: str
    id: str
    field: str

class LinkContentResponse(BaseModel):
    name: str
    id: str
    field: str
    created_at: Optional[str] = None
    indexing_status: str
    status_code: int
    message: Optional[str] = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query_result: str

class FileUploadResponse(BaseModel):
    status: str
    message: str
    body: Dict[str, str]

class UnlinkContentResponse(BaseModel):
    file_id: str
    status_code: int
    message: str

class CreateConfigRequest(BaseModel):
    pass

class CreateConfigResponse(BaseModel):
    message: str
    config_id: str

