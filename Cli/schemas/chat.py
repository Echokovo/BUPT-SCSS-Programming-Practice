from typing import Optional, List, Union

from pydantic import BaseModel

class Message(BaseModel):
    type : str
    content : str

class UserChat(BaseModel):
    friend_id: str
    message: Message

class UserChatRequest(BaseModel):
    data: UserChat

class UserHistory(BaseModel):
    friend_id: str

class UserHistoryRequest(BaseModel):
    data: UserHistory

class UserDecipher(BaseModel):
    timestamp: int

class UserDecipherRequest(BaseModel):
    data: UserDecipher

class FullMessage(BaseModel):
    timestamp: int
    sender: str
    receiver: str
    message: Message

class History(BaseModel):
    length: int
    messages: List[FullMessage]

class PlainText(BaseModel):
    plain_text: str

class BaseResponse(BaseModel):
    status: int
    message: str
    data: Optional[Union[History, PlainText]] = None