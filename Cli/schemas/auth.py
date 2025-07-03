from typing import Optional, Any

from pydantic import BaseModel, Field, ValidationError, model_validator
import re

class UserRegister(BaseModel):
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

class UserRegisterRequest(BaseModel):
    data: UserRegister

class UserLogin(BaseModel):
    user_id: str
    password: str

class UserLoginRequest(BaseModel):
    data: UserLogin

class Token(BaseModel):
    token: str

class BaseResponse(BaseModel):
    status: int
    message: str
    data: Optional[Token] = None