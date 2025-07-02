from typing import List
from pydantic import BaseModel

class Contact(BaseModel):
    user_id: str
    flag: bool

class AddFriendRequest(BaseModel):
    friend_id: str

class RemoveFriendRequest(BaseModel):
    friend_id: str

class GetContactsResponse(BaseModel):
    contacts: List[Contact]