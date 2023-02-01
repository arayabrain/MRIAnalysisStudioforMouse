from . import code

MSG = {
    code.E_SUCCESS: 'success',
    code.E_FAIL: 'fail',
    code.E_AUTH: 'Not authenticated',
    code.E_AUTH_TOKEN_CHECK_FAIL: 'Can not verify your credentials',
    code.E_AUTH_TOKEN_TYPE_INVALID: 'Invalid token type',
    code.E_AUTH_TOKEN_TIMEOUT: 'Your token has expired',
    code.E_AUTH_USERPASSWD_INVALID: 'Your username or password is invalid',
    code.E_USER_INACTIVE: 'User is inactive',
    code.E_USER_MISS_PERM: 'User does not have enough permission',
    code.E_USER_C_USER_EXIST: 'User is already existed',
    code.E_USER_R_NOTFOUND: 'User not found',
    code.E_USER_U_PASSWORD_NOTMATCH: 'The password does not match',
    code.E_USER_U_INFO_INTERNAL: 'Internal error when updating' 'user information',
}
