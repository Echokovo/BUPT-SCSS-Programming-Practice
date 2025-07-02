from typing import Optional

from pydantic import BaseModel, Field, ValidationError, model_validator
import re

class UserRegisterRequest(BaseModel):
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    password: str
    email: str

    @model_validator(mode='after')
    def validate_user_id(self):
        if not re.fullmatch(r'\w+', self.user_id):
            raise ValidationError('user_id 只能包含字母、数字和下划线')
        return self

class UserLoginRequest(BaseModel):
    user_id: str
    password: str
    public_key: str
    ip: str
    port: int

class UserRegisterResponse(BaseModel):
    status: int
    message: str

class Token(BaseModel):
    token: str

class UserLoginResponse(BaseModel):
    status: int
    message: str
    data: Optional[Token]