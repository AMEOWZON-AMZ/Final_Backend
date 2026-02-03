from pydantic import BaseModel
from typing import Any, Optional, Dict, List
from datetime import datetime


class ApiError(BaseModel):
    """에러 정보 구조"""
    code: Optional[str] = None
    message: str
    details: Optional[Dict[str, Any]] = None


class BaseResponse(BaseModel):
    """통일된 API 응답 구조 - 프론트엔드 친화적"""
    success: bool
    data: Optional[Any] = None
    error: Optional[ApiError] = None
    timestamp: str


class PaginationMeta(BaseModel):
    """페이지네이션 메타데이터"""
    page: int
    limit: int
    total: int
    has_next: bool
    has_prev: bool
    total_pages: int


# API 응답 헬퍼 함수들 - 프론트엔드 친화적 구조
def success_response(data: Any = None) -> Dict[str, Any]:
    """성공 응답 생성 - { success, data, error } 구조 통일"""
    return {
        "success": True,
        "data": data,
        "error": None,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(
    message: str, 
    error_code: str = None, 
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """에러 응답 생성 - { success, data, error } 구조 통일"""
    return {
        "success": False,
        "data": None,
        "error": {
            "code": error_code,
            "message": message,
            "details": details
        },
        "timestamp": datetime.utcnow().isoformat()
    }


def paginated_response(
    data: List[Any], 
    page: int, 
    limit: int, 
    total: int
) -> Dict[str, Any]:
    """페이지네이션된 응답 생성 - 통일된 구조"""
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "items": data,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "total_pages": total_pages
            }
        },
        "error": None,
        "timestamp": datetime.utcnow().isoformat()
    }