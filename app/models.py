from typing import List, Optional
from pydantic import BaseModel

class Order(BaseModel):
    id: int
    title: str
    description: str

class CreateResponse(BaseModel):
    order_id: str

class ReadResponse(BaseModel):
    items: Optional[List[Order]] = None
    from_cache: bool = False

class UpdateResponse(BaseModel):
    order_id: str

class DeleteResponse(BaseModel):
    order_id: str

class ErrorResponse(BaseModel):
    message: str