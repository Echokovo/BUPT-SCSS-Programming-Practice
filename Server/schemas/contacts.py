from typing import List, Optional
from pydantic import BaseModel

class AddFriend(BaseModel):
    friend_id: str

class AddFriendRequest(BaseModel):
    data: AddFriend

class DeleteFriend(BaseModel):
    friend_id: str

class DeleteFriendRequest(BaseModel):
    data: DeleteFriend

class Contact(BaseModel):
    user_id: str
    flag: bool

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