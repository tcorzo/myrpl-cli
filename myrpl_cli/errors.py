class AuthError(BaseException):
    pass


class MissingCredentialsError(AuthError):
    pass
