from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class TableBase(BaseModel):
    name: str
    seats: int
    location: Optional[str] = None

class TableCreate(TableBase):
    pass

class TableResponse(TableBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
