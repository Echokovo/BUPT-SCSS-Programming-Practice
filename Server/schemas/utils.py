from typing import Optional

from pydantic import BaseModel

class GetStateRequest(BaseModel):
    friend_id: str

class GetPublicKeyRequest(BaseModel):
    friend_id: str

class GetStateResponse(BaseModel):
    status: int
    message: str

class PublicKey(BaseModel):
    public_key: str

class GetPublicKeyResponse(BaseModel):
    status: int
    message: str
    data: Optional[PublicKey]