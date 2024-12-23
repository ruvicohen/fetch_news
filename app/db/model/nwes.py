from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.db.model.location import Location


class News(BaseModel):
    title: Optional[str]
    body: Optional[str]
    time: Optional[datetime]
    classification: Optional[str]
    location: Optional[Location]
