from enum import Enum


class ErrorType(Enum):
    USER_NOT_FOUND = ("User not found", 404)
    INVALID_CREDENTIALS = ("Invalid credentials", 401)
    PERMISSION_DENIED = ("Permission denied", 403)
    BAD_REQUEST = ("Bad request", 400)
    SERVER_ERROR = ("Internal server error", 500)

    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
