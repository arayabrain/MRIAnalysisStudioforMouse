from typing import Optional

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from backend.core import settings
from backend.core.security import validate_access_token
from backend.service.firebase.crud_user import read_user


async def get_current_user(
    res: Response,
    ex_token: Optional[str] = Depends(APIKeyHeader(name='ExToken', auto_error=False)),
    credential: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
):
    if settings.USE_FIREBASE_TOKEN:
        if credential is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={'WWW-Authenticate': 'Bearer realm="auth_required"'},
            )
        try:
            user = auth.verify_id_token(credential.credentials)
            user = await read_user(user_id=user['uid'])
            return user.dict()
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials",
                headers={'WWW-Authenticate': 'Bearer error="invalid_token"'},
            )

    if ex_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer realm="auth_required"'},
        )
    payload, e = validate_access_token(ex_token)
    if e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e)
    res.headers['WWW-Authenticate'] = 'Bearer realm="auth_required"'
    try:
        user = await read_user(user_id=payload['sub'])
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return user.dict()


def get_current_admin_user(current_user=Depends(get_current_user)):
    if current_user.get('role') == 1:
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Insufficient privileges',
        )
