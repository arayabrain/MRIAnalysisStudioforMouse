from fastapi import APIRouter, Depends
from firebase_admin import auth

from backend.deps import get_current_user
from backend.models.stat_image import StatImageParam
from backend.models.user import User

router = APIRouter()


@router.get("/stat_image", response_model=StatImageParam)
async def get_stat_image_param(current_user: User = Depends(get_current_user)):
    user = auth.get_user(current_user['uid'])
    current_claims = user.custom_claims
    return StatImageParam(**current_claims)


@router.post("/stat_image", response_model=StatImageParam)
async def set_stat_image_param(
    data: StatImageParam, current_user: User = Depends(get_current_user)
):
    user = auth.get_user(current_user['uid'])
    current_claims = user.custom_claims
    current_claims.update(data.dict())
    auth.set_custom_user_claims(user.uid, current_claims)
    return StatImageParam(**current_claims)
