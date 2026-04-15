class AuthException(Exception):
    pass

class UserNotFoundError(AuthException):
    pass

class InvalidCredentialsError(AuthException):
    pass

class UsernameAlreadyExistsError(AuthException):
    pass

class InvalidTokenError(AuthException):
    pass

class TokenRevokedError(AuthException):
    pass