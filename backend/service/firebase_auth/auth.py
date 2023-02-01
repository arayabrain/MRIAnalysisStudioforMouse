import json
from http import HTTPStatus

from firebase_admin import auth
from firebase_admin._auth_utils import EmailAlreadyExistsError
from requests.exceptions import HTTPError

from backend.models import Token, User, UserAuth
from backend.models.error import code, make_response


async def register(email: str, password: str):
    # try:\
    user = auth.create_user(email=email, password=password)
    user = User(uid= user.uid, email=user.email, display_name=user.display_name)
    # except EmailAlreadyExistsError as e:
    #     return None, make_response(HTTPStatus.BAD_REQUEST, code.E_FAIL, detail=e.default_message)
    # except Exception as e:
    #     return None, make_response(HTTPStatus.INTERNAL_SERVER_ERROR, code.E_FAIL)
    # return user, None
    return user

async def delete_user(user: UserAuth):
    auth.delete_user(user.uid)


async def authenticate(user: UserAuth):
    try:
        from . import pb
        user = pb.auth().sign_in_with_email_and_password(user.email, user.password)
        jwt = user['idToken']
        token = Token(access_token=jwt, token_type='bearer')
    except:
        return None, make_response(HTTPStatus.INTERNAL_SERVER_ERROR, code.E_FAIL)
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