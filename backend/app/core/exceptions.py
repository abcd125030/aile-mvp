"""Application-level HTTP exceptions."""

from fastapi import HTTPException, status


class AppHTTPException(HTTPException):
    """Unified HTTP exception type for service/repository layers."""

    def __init__(self, *, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail=detail)


def bad_request(detail: str) -> AppHTTPException:
    return AppHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def unauthorized(detail: str = "未提供有效的访问令牌") -> AppHTTPException:
    return AppHTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def forbidden(detail: str) -> AppHTTPException:
    return AppHTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def not_found(detail: str) -> AppHTTPException:
    return AppHTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
