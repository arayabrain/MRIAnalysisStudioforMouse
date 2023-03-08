from fastapi import APIRouter, Depends

from backend.deps import get_current_admin_user
from backend.models.user import UserCreate, UserUpdate
from backend.service import firebase


router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_admin_user)])
async def get_list(next_page_token: str = None, limit: int = 10):
    return await firebase.list_user(next_page_token, limit)


@router.post("/", dependencies=[Depends(get_current_admin_user)])
async def create_user(data: UserCreate):
    return await firebase.create_user(data)


@router.get("/{user_id}", dependencies=[Depends(get_current_admin_user)])
async def read_user(user_id: str):
    return await firebase.read_user(user_id)


@router.put("/{user_id}", dependencies=[Depends(get_current_admin_user)])
async def update_user(user_id: str, data: UserUpdate):
    return await firebase.update_user(user_id, data)


@router.delete("/{user_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_user(user_id: str):
    return await firebase.delete_user(user_id)
