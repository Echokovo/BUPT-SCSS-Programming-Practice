from pydantic import BaseModel

class GetStateRequest(BaseModel):
    friend_id: str

class GetPublicKeyRequest(BaseModel):
    friend_id: str

class GetPublicKeyResponse(BaseModel):
    public_key: str