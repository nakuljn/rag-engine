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

class LinkContentRequest(BaseModel):
    pass

class UnlinkContentRequest(BaseModel):
    pass

class QueryRequest(BaseModel):
    pass

class QueryResponse(BaseModel):
    query_result: str

class BatchReadRequest(BaseModel):
    pass

class BatchReadResponse(BaseModel):
    files_status: str

class CreateConfigRequest(BaseModel):
    pass

class CreateConfigResponse(BaseModel):
    message: str
    config_id: str

class FileUploadRequest(BaseModel):
    name: str
    type: str
    uploaded_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class FileUpdateRequest(BaseModel):
    name: str
    type: str
    uploaded_at: datetime
    metadata: Optional[Dict[str, Any]] = None