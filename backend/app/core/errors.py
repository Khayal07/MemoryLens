"""Typed application errors + a consistent JSON error envelope:
    {"error": {"code": "...", "message": "..."}}
Services raise these; the API translates them to HTTP responses in main.py."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class RateLimitedError(AppError):
    status_code = 429
    code = "rate_limited"


def _envelope(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return _envelope(exc.status_code, exc.code, exc.message)
