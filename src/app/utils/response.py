from typing import Any

from starlette.responses import JSONResponse


def response(
    code: int = 0, message: str = "success", data: Any | None = None, status_code: int = 200, **kwargs
) -> JSONResponse:
    resp = {
        "code": code,
        "message": message,
        "data": data,
        **kwargs,
    }
    return JSONResponse(content=resp, status_code=status_code)
