from typing import List, Optional
from pydantic import BaseModel

class Contact(BaseModel):
    user_id: str
    flag: bool

class AddFriendRequest(BaseModel):
    friend_id: str

class DeleteFriendRequest(BaseModel):
    friend_id: str

class GetContactsResponse(BaseModel):
    status: int
    message: str
    data: Optional[List[Contact]]

class AddFriendResponse(BaseModel):
    status: int
    message: str

class DeleteFriendResponse(BaseModel):
    status: int
    message: str