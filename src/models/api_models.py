from pydantic import BaseModel
from typing import List, Optional, Any

# Collection Models
class CreateCollectionRequest(BaseModel):
    """Request model for creating a collection"""
    # Placeholder - will be filled with actual fields later
    pass

class CreateCollectionResponse(BaseModel):
    """Response model for creating a collection"""
    message: str
    collection_id: str

class CollectionStatusRequest(BaseModel):
    """Request model for collection status"""
    # Placeholder - will be filled with actual fields later
    pass

# Content Models
class LinkContentRequest(BaseModel):
    """Request model for linking content to collection"""
    # Placeholder - will be filled with actual fields later
    pass

class UnlinkContentRequest(BaseModel):
    """Request model for unlinking content from collection"""
    # Placeholder - will be filled with actual fields later
    pass

# Query Models
class QueryRequest(BaseModel):
    """Request model for querying collection"""
    # Placeholder - will be filled with actual fields later
    pass

class QueryResponse(BaseModel):
    """Response model for query results"""
    query_result: str

class BatchReadRequest(BaseModel):
    """Request model for batch reading files"""
    # Placeholder - will be filled with actual fields later
    pass

class BatchReadResponse(BaseModel):
    """Response model for batch read results"""
    files_status: str

# Config Models
class CreateConfigRequest(BaseModel):
    """Request model for creating config"""
    # Placeholder - will be filled with actual fields later
    pass

class CreateConfigResponse(BaseModel):
    """Response model for creating config"""
    message: str
    config_id: str