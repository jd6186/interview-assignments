from pydantic import BaseModel
from typing import Any, Optional
from common.error_types import ErrorType


class ResponseDto(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    total_count: Optional[int] = None
    status_code: Optional[int] = None  # 상태 코드 추가

    @staticmethod
    def success_response(data: Any = None, total_count: int = None):
        return ResponseDto(success=True, message="success", data=data, total_count=total_count, status_code=200)

    @staticmethod
    def error_response(error_type: ErrorType):
        return ResponseDto(success=False, message=error_type.message, status_code=error_type.status_code)
