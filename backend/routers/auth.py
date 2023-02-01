from fastapi import APIRouter, Depends
from sqlmodel import Session
from fastapi.responses import JSONResponse
from backend.core.security import get_current_user
from backend.models import Token, User, UserAuth
from backend.models.user import UserDB, UserSendResetPasswordEmail, UserVerifyResetPasswordCode
from backend.service import firebase_auth
from backend.shared.database import get_db


router = APIRouter()


@router.post("/register")
async def register(user_data: UserAuth, db: Session = Depends(get_db)):
    userDB = None
    try:
        user = await firebase_auth.register(user_data.email, user_data.password)
        userDB = UserDB.from_orm(user)
        db.add(userDB)
        await db.commit()
        await db.refresh(userDB)
    except Exception as e:
        if user:
            await firebase_auth.delete_user(user.uid)
        await db.rollback()
        return JSONResponse(
            content={"message": str(e)},
            status_code=400
        )
    return userDB


@router.get("/me", response_model=User)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/login", response_model=Token)
async def login(user: UserAuth, db: Session = Depends(get_db),):
    token, err = await firebase_auth.authenticate(user=user)
    if err:
        return err
    return token


@router.post("/send-reset-password-email")
async def send_reset_password_email(data: UserSendResetPasswordEmail):
    return await firebase_auth.send_password_reset_email(data.email)


@router.post("/verify-reset-password-code")
async def send_reset_password_email(data: UserVerifyResetPasswordCode):
    return await firebase_auth.verify_password_reset_code(data.reset_code, data.new_password)
