"""
공통 베이스 스키마
모든 Pod에서 사용하는 기본 Pydantic 스키마들
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Generic, TypeVar, List
from enum import Enum


class BaseSchema(BaseModel):
    """모든 스키마의 기본 클래스"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )


class TimestampSchema(BaseSchema):
    """타임스탬프 스키마"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ResponseStatus(str, Enum):
    """응답 상태 열거형"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class BaseResponse(BaseSchema):
    """기본 응답 스키마"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


T = TypeVar('T')


class DataResponse(BaseResponse, Generic[T]):
    """데이터 포함 응답 스키마"""
    data: Optional[T] = None


class ListResponse(BaseResponse, Generic[T]):
    """리스트 응답 스키마"""
    data: List[T] = []
    total: int = 0
    page: int = 1
    size: int = 10
    has_next: bool = False


class ErrorResponse(BaseResponse):
    """에러 응답 스키마"""
    status: ResponseStatus = ResponseStatus.ERROR
    error_code: Optional[str] = None
    details: Optional[dict] = None


class PaginationParams(BaseSchema):
    """페이지네이션 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    size: int = Field(default=10, ge=1, le=100, description="페이지 크기")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class SortParams(BaseSchema):
    """정렬 파라미터"""
    sort_by: str = Field(default="created_at", description="정렬 필드")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="정렬 순서")


class FilterParams(BaseSchema):
    """필터 파라미터"""
    search: Optional[str] = Field(default=None, description="검색어")
    is_active: Optional[bool] = Field(default=None, description="활성 상태")
    created_from: Optional[datetime] = Field(default=None, description="생성일 시작")
    created_to: Optional[datetime] = Field(default=None, description="생성일 종료")