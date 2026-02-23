from typing import Any, Optional, Dict
from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseResponse):
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """성공 응답 생성"""
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(
    message: str = "Error occurred",
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """에러 응답 생성"""
    response = {
        "success": False,
        "message": message
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details:
        response["details"] = details
    
    return response