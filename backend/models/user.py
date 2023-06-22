from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class Role(BaseModel):
    code: int
    name: str


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    display_name: str = Field(max_length=100)
    lab: str = Field(max_length=100)
    role: int
    email: EmailStr
    password: str = Field(
        max_length=255, regex='^(?=.*\d)(?=.*[!#$%&()*+,-./@_|])(?=.*[a-zA-Z]).{6,255}$'
    )

    class Config:
        anystr_strip_whitespace = True

    @validator('email')
    def email_must_less_than_255(cls, value):
        if len(value) >= 255:
            raise ValueError("Email too long")
        return value

    @validator('lab', 'display_name')
    def check_empty_string(cls, value: str):
        if not value.strip():
            raise ValueError('Value cannot be empty')
        return value.strip()


class UserUpdate(BaseModel):
    display_name: str = Field(max_length=100)
    lab: str = Field(max_length=100)
    role: int

    class Config:
        anystr_strip_whitespace = True

    @validator('lab', 'display_name')
    def check_empty_string(cls, value: str):
        if not value.strip():
            raise ValueError('Value cannot be empty')
        return value.strip()


class UserUpdateName(BaseModel):
    display_name: str = Field(max_length=100)


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(
        max_length=255, regex='^(?=.*\d)(?=.*[!#$%&()*+,-./@_|])(?=.*[a-zA-Z]).{6,255}$'
    )


class User(BaseModel):
    uid: str
    email: EmailStr
    display_name: Optional[str]
    created_time: Optional[datetime] = None
    role: Optional[int]
    lab: Optional[str]
    last_login_time: Optional[datetime] = None


class UserSendResetPasswordEmail(BaseModel):
    email: EmailStr


class UserVerifyResetPasswordCode(BaseModel):
    reset_code: str
    new_password: str = Field(max_length=255)


class ListUserPaging(BaseModel):
    data: Optional[List[User]]
    total_page: Optional[int]
