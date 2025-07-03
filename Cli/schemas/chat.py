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