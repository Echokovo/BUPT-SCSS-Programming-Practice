from typing import List, Optional, Dict
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
    flag: int

class BaseResponse(BaseModel):
    status: int
    message: str
    data: Optional[Dict[str,List[Contact]]] = None