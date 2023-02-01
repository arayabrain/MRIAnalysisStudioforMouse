from fastapi import Request
from fastapi.responses import JSONResponse

from . import msg


class AppException(Exception):
    def __init__(self, status_code: int, code: int, detail: str = None):
        self.status_code = status_code
        self.code = code
        self.detail = detail

    def as_message(self):
        """
        TODO: missing function docstring
        """
        return (
            f'<AppException:status_code={self.status_code}, '
            f'code={self.code}, '
            f'message={msg.MSG.get(self.code, "Fail")}>'
        )


def make_response(status_code: int, code: int, detail: str = None) -> JSONResponse:
    """
    TODO: missing function docstring
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": msg.MSG.get(code, 'Fail'),
            'detail': detail,
        },
    )


def exception_handler(_: Request, exc: AppException):
    """
    TODO: missing function docstring
    """
    return make_response(exc.status_code, exc.code, exc.detail)
