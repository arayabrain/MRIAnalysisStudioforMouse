from fastapi import HTTPException
from firebase_admin import auth

from backend.models import User
from backend.models.user import UserCreate, UserUpdate, ListUserPaging


async def list_user(next_page_token: str = None, limit: int = 10):
    try:
        result = auth.list_users(max_results=limit, page_token=next_page_token)
        users = result.users
        data = [
            User(
                uid=user.uid,
                email=user.email,
                display_name=user.display_name,
                role=user.custom_claims.get('role') if user.custom_claims else None
            )
            for user in users
        ]
        if not result.has_next_page:
            next_page_token = None
        else:
            next_page_token = result.next_page_token

        total = auth.list_users()
        import math
        total_page = math.ceil(len(total.users) / limit)
        return ListUserPaging(data=data, next_page_token=next_page_token, total_page=total_page)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def create_user(data: UserCreate):
    try:
        user_data = data.dict()
        role_data = user_data.pop('role')

        user = auth.create_user(**user_data)
        auth.set_custom_user_claims(user.uid, {'role': role_data})
        return User(uid=user.uid, email=user.email, display_name=user.display_name, role=role_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {e}")


async def read_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        role = user.custom_claims.get('role') if user.custom_claims else None
        return User(uid=user.uid, email=user.email, display_name=user.display_name, role=role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def update_user(user_id: str, data: UserUpdate):
    try:
        user_data = data.dict(exclude_unset=True)
        role_data = user_data.pop('role')

        auth.set_custom_user_claims(user_id, {'role': role_data})
        user = auth.update_user(user_id, **user_data)
        role = user.custom_claims.get('role') if user.custom_claims else None
        return User(uid=user.uid, email=user.email, display_name=user.display_name, role=role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def delete_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        role = user.custom_claims.get('role') if user.custom_claims else None

        auth.delete_user(user.uid)
        return User(uid=user.uid, email=user.email, display_name=user.display_name, role=role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
