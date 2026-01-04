from starlette.responses import JSONResponse


class BaseAPIException(Exception):
    status_code = 200
    error_code = -1
    message = "服务器未知错误"

    def __init__(self, status_code=None, message=None, error_code=None):
        if status_code:
            self.status_code = status_code
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code

        super(BaseAPIException, self).__init__(self.message)

    def response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={
                "code": self.error_code,
                "message": self.message,
            },
        )


class UnknownException(BaseAPIException):
    code = 500


class ContentTypeException(BaseAPIException):
    error_code = -2
    message = "不支持的content-type类型"


class ParameterException(BaseAPIException):
    error_code = 1002
    message = "参数错误"


# -------------用户-------------
class UserExistException(BaseAPIException):
    error_code = 2001
    message = "用户已存在"


class UserNotExistException(BaseAPIException):
    error_code = 2002
    message = "用户不存在"


class PasswordException(BaseAPIException):
    error_code = 2003
    message = "用户名或密码错误"


class ActiveException(BaseAPIException):
    error_code = 2004
    message = "用户未激活"


class PermissionException(BaseAPIException):
    error_code = 2005
    message = "认证失败，没有找到令牌"


class InvalidTokenException(BaseAPIException):
    error_code = 2006
    message = "令牌不合法"


class InvalidAccessTokenException(BaseAPIException):
    # 错误把refresh-token当成access-token使用的情况
    error_code = 20061
    message = "令牌不合法"


class ExpiredTokenException(BaseAPIException):
    error_code = 2007
    message = "令牌已过期"


class EmailExistException(BaseAPIException):
    error_code = 2008
    message = "邮箱已被注册"


class RefreshException(BaseAPIException):
    error_code = 2010
    message = "更新令牌失败"


# -------------用户-------------


# -------------角色-------------
class RoleExistException(BaseAPIException):
    error_code = 3001
    message = "角色已存在"


class RoleNotExistException(BaseAPIException):
    error_code = 3002
    message = "角色不存在"


class RoleHasUserException(BaseAPIException):
    error_code = 3003
    message = "角色下存在用户，不可删除"


# -------------角色-------------


# -------------文件-------------
class ResourceNotExistException(BaseAPIException):
    error_code = 4001
    message = "资源不存在"


class ResourceExistException(BaseAPIException):
    error_code = 4002
    message = "资源已存在"


class ResourceConstraintException(BaseAPIException):
    error_code = 4003
    message = "资源被引用，不能删除"


# -------------文件-------------


# -------------任务-------------
class JobNotExistException(BaseAPIException):
    error_code = 5001
    message = "任务不存在"


class JobNotRetryException(BaseAPIException):
    error_code = 5002
    message = "只能重试执行失败的任务"


class JobTypeErrorException(BaseAPIException):
    error_code = 5003
    message = "任务类型无效"


class OneClickErrorException(BaseAPIException):
    error_code = 5004
    message = "一键任务为空"


# -------------任务-------------
