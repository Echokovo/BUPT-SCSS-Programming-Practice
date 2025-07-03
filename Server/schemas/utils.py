from typing import Optional

from pydantic import BaseModel

class GetState(BaseModel):
    friend_id: str

class GetStateRequest(BaseModel):
    data: GetState

class PublicKey(BaseModel):
    public_key: str

class BaseResponse(BaseModel):
    status: int
    message: str
    data: Optional[PublicKey] = None