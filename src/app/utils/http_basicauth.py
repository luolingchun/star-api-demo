import inspect
from functools import wraps

from app.config import BASIC_AUTH_PASSWORD, BASIC_AUTH_USERNAME
from app.utils.exceptions import PasswordException


def basic_required(func):
    """HTTP Basic装饰器"""

    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        auth = request.headers.get("Authorization")
        is_passed = False

        if auth and auth.startswith("Basic "):
            import base64

            # 解码 Basic Auth
            encoded_credentials = auth.split(" ", 1)[1]
            decoded_bytes = base64.b64decode(encoded_credentials)
            decoded_str = decoded_bytes.decode("utf-8")
            username, password = decoded_str.split(":", 1)
            is_passed = username == BASIC_AUTH_USERNAME and password == BASIC_AUTH_PASSWORD

        if not is_passed:
            raise PasswordException()

        if "request" in inspect.signature(func).parameters:
            kwargs["request"] = request

        return await func(request, *args, **kwargs)

    return wrapper
