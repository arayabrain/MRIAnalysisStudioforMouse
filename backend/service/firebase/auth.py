import json
from http import HTTPStatus

from firebase_admin import auth, exceptions
from requests.exceptions import HTTPError

from backend.models import Token, UserAuth
from backend.models.error import AppException, code, make_response


async def register(email: str, password: str, role: str = None, lab: str = None):
    try:
        user = auth.create_user(email=email, password=password)
        user_claims = {'role': role, 'lab': lab}
        auth.set_custom_user_claims(user.uid, user_claims)
    except exceptions.FirebaseError as exc:
        if exc.code == 'ALREADY_EXISTS':
            return None, AppException(HTTPStatus.BAD_REQUEST, code.E_USER_C_USER_EXIST, detail=str(exc))
        return None, AppException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, code=code.E_AUTH, detail=str(exc))
    return user, None


async def authenticate(user: UserAuth):
    try:
        from . import pb
        user = pb.auth().sign_in_with_email_and_password(user.email, user.password)
        access_token = user['idToken']
        refresh_token = user['refreshToken']
        token = Token(access_token=access_token, refresh_token=refresh_token, token_type='bearer')
    except Exception as e:
        return None, make_response(HTTPStatus.INTERNAL_SERVER_ERROR, code.E_FAIL, str(e))
    return token, None


async def send_password_reset_email(email: str):
    status_code = HTTPStatus.OK
    _code = code.E_SUCCESS
    detail = None
    try:
        from . import pb
        pb.auth().send_password_reset_email(email)
    except HTTPError as e:
        err = json.loads(e.strerror)
        status_code = HTTPStatus.BAD_REQUEST
        _code = code.E_FAIL
        detail = err['error']['message']
    except Exception as e:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        _code = code.E_FAIL
    return make_response(status_code, _code, detail)


async def verify_password_reset_code(reset_code: str, new_password: str):
    status_code = HTTPStatus.OK
    _code = code.E_SUCCESS
    detail = None
    try:
        from . import pb
        pb.auth().verify_password_reset_code(reset_code, new_password)
    except HTTPError as e:
        err = json.loads(e.strerror)
        status_code = HTTPStatus.BAD_REQUEST
        _code = code.E_FAIL
        detail = err['error']['message']
    except Exception as e:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        _code = code.E_FAIL
    return make_response(status_code, _code, detail)