from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    region: Optional[str]
    country: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]