from http import HTTPStatus
from typing import Tuple, List
from sqlmodel import Session

from backend.models.error import AppException, code
from backend.models.user import (
    User,
    UserAuth,
    UserDB,
)
from backend.service.util import get_multi as _get_multi
from backend.service.util import get_one


# ======= Fetching Section Begin =======
async def get_by_email(
    db: Session,
    email: str,
) -> Tuple[UserDB, AppException]:
    """
    TODO: missing function docstring
    """
    user = await get_one(db, UserDB, email=email)
    err = (
        AppException(HTTPStatus.NOT_FOUND, code.E_USER_R_NOTFOUND)
        if user is None
        else None
    )
    return user, err


# pylint:disable=redefined-builtin
async def get_by_id(
    db: Session,
    id: int,
) -> Tuple[UserDB, AppException]:
    """
    TODO: missing function docstring
    """
    user = await get_one(db, UserDB, id=id)
    err = (
        AppException(HTTPStatus.NOT_FOUND, code.E_USER_R_NOTFOUND)
        if user is None
        else None
    )
    return user, err


async def get_multi(
    db: Session, offset: int = 0, limit: int = 10
) -> Tuple[List[User], AppException]:
    """
    TODO: missing function docstring
    """
    return await _get_multi(db, UserDB, offset, limit)


# ======= Fetching Section End =======


# ======= Creating Section Begin =======
async def create_user_ex(
    db: Session,
    user_data: UserAuth,
) -> Tuple[UserDB, AppException]:
    """
    TODO: missing function docstring
    """
    try:
        user = UserDB.from_orm(user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except Exception:
        return None, AppException(HTTPStatus.INTERNAL_SERVER_ERROR, code.E_FAIL)
    return user, None


async def create_user(
    db: Session,
    user_data: User,
) -> Tuple[UserDB, AppException]:
    """
    TODO: missing function docstring
    """
    user_data_ex = User.from_orm(user_data)
    return await create_user_ex(db, user_data_ex)



async def delete(
    db: Session,
    user: UserDB,
) -> Tuple[bool, AppException]:
    """
    TODO: missing function docstring
    """
    try:
        await db.delete(user)
        await db.commit()
    except Exception:
        return None, AppException(
            HTTPStatus.INTERNAL_SERVER_ERROR, code.E_USER_U_INFO_INTERNAL
        )

    return True, None


# ======= Creating Section End =======
