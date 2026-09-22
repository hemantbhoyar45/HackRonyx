from pydantic import BaseModel
from typing import Optional

class WaterBodyBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

class WaterBodyCreate(WaterBodyBase):
    geojson_polygon: dict  # Will hold AOI polygon

class WaterBody(WaterBodyBase):
    id: str

    class Config:
        from_attributes = True
