from datetime import datetime
from typing import Optional
from sqlalchemy.sql.functions import current_timestamp

from sqlmodel import Field, SQLModel
from pydantic import EmailStr

class UserAuth(SQLModel):
    email: EmailStr
    password: str


class User(SQLModel):
    uid: str
    email: EmailStr
    display_name: Optional[str]
    created_time: Optional[datetime] = None
    last_login_time: Optional[datetime] = None


class UserDB(User, table=True):
    __tablename__ = 'user'

    uid: str = Field(default=None, primary_key=True)
    password: Optional[str] = None
    created_time: Optional[datetime] = Field(
        nullable=False,
        index=True,
        sa_column_kwargs={'server_default': current_timestamp()},
    )
    last_login_time: Optional[datetime] = Field(default=None, nullable=True, index=True)

class UserSendResetPasswordEmail(SQLModel):
    email: EmailStr

class UserVerifyResetPasswordCode(SQLModel):
    reset_code: str
    new_password: str