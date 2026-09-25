from datetime import datetime
from pydantic import BaseModel, Field

class HostedZoneCreate(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str = Field(default="", max_length=500)
    zone_type: str = Field(default="Public")

class HostedZoneUpdate(HostedZoneCreate):
    pass

class HostedZoneOut(BaseModel):
    id: int
    name: str
    zone_id: str
    description: str
    zone_type: str
    created_at: datetime
    record_count: int = 0
    model_config = {"from_attributes": True}

class PaginatedZones(BaseModel):
    items: list[HostedZoneOut]
    page: int
    page_size: int
    total: int
    pages: int
