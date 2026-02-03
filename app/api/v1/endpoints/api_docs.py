from fastapi import APIRouter
from app.schemas.response import success_response

router = APIRouter()


@router.get("/endpoints")
async def get_api_endpoints():
    """프론트엔드에서 사용할 수 있는 모든 API 엔드포인트 목록"""
    
    endpoints = {
        "auth": {
            "base_url": "/api/v1/auth",
            "endpoints": {
                "social_login": {
                    "method": "POST",
                    "path": "/social",
                    "description": "소셜 로그인 (카카오, 구글, 네이버, 애플)",
                    "requires_auth": False,
                    "request_body": {
                        "provider": "string (kakao|google|naver|apple)",
                        "access_token": "string"
                    },
                    "response": {
                        "success": "boolean",
                        "message": "string",
                        "data": {
                            "access_token": "string",
                            "token_type": "string",
                            "expires_in": "number",
                            "user": "object"
                        }
                    }
                },
                "dev_token": {
                    "method": "POST",
                    "path": "/dev-token",
                    "description": "개발용 토큰 생성 (테스트용)",
                    "requires_auth": False,
                    "request_body": {
                        "user_id": "string",
                        "email": "string (optional)",
                        "provider": "string (default: kakao)"
                    }
                },
                "get_me": {
                    "method": "GET",
                    "path": "/me",
                    "description": "현재 로그인한 사용자 정보 조회",
                    "requires_auth": True
                },
                "refresh_token": {
                    "method": "POST",
                    "path": "/refresh",
                    "description": "토큰 갱신",
                    "requires_auth": True
                },
                "logout": {
                    "method": "POST",
                    "path": "/logout",
                    "description": "로그아웃",
                    "requires_auth": True
                }
            }
        },
        "users": {
            "base_url": "/api/v1/users",
            "endpoints": {
                "get_my_profile": {
                    "method": "GET",
                    "path": "/me",
                    "description": "내 프로필 정보 조회",
                    "requires_auth": True,
                    "response": {
                        "success": "boolean",
                        "message": "string",
                        "data": {
                            "id": "number",
                            "email": "string",
                            "username": "string",
                            "full_name": "string",
                            "nickname": "string",
                            "profile_image_url": "string",
                            "bio": "string",
                            "provider": "string"
                        }
                    }
                },
                "update_my_profile": {
                    "method": "PUT",
                    "path": "/me",
                    "description": "내 프로필 정보 수정",
                    "requires_auth": True,
                    "request_body": {
                        "username": "string (optional)",
                        "full_name": "string (optional)",
                        "nickname": "string (optional)",
                        "bio": "string (optional)",
                        "phone_number": "string (optional)",
                        "profile_image_url": "string (optional)"
                    }
                },
                "search_users": {
                    "method": "GET",
                    "path": "/search",
                    "description": "사용자 검색",
                    "requires_auth": True,
                    "query_params": {
                        "q": "string (required, min 2 chars)",
                        "page": "number (optional, default 1)",
                        "limit": "number (optional, default 10, max 50)"
                    },
                    "response": {
                        "success": "boolean",
                        "message": "string",
                        "data": "array of users",
                        "meta": {
                            "page": "number",
                            "limit": "number",
                            "total": "number",
                            "has_next": "boolean",
                            "has_prev": "boolean",
                            "total_pages": "number"
                        }
                    }
                },
                "get_user_profile": {
                    "method": "GET",
                    "path": "/{user_id}",
                    "description": "다른 사용자 프로필 조회",
                    "requires_auth": True,
                    "path_params": {
                        "user_id": "number"
                    }
                },
                "get_my_friends": {
                    "method": "GET",
                    "path": "/me/friends",
                    "description": "내 친구 목록 조회",
                    "requires_auth": True,
                    "response": {
                        "success": "boolean",
                        "message": "string",
                        "data": {
                            "friends": "array",
                            "total": "number"
                        }
                    }
                },
                "add_friend": {
                    "method": "POST",
                    "path": "/me/friends",
                    "description": "친구 추가",
                    "requires_auth": True,
                    "request_body": {
                        "friend_id": "string"
                    }
                },
                "remove_friend": {
                    "method": "DELETE",
                    "path": "/me/friends/{friend_id}",
                    "description": "친구 삭제",
                    "requires_auth": True,
                    "path_params": {
                        "friend_id": "string"
                    }
                }
            }
        },
        "health": {
            "base_url": "/health",
            "endpoints": {
                "basic_health": {
                    "method": "GET",
                    "path": "/",
                    "description": "기본 헬스체크",
                    "requires_auth": False
                },
                "detailed_health": {
                    "method": "GET",
                    "path": "/detailed",
                    "description": "상세 헬스체크",
                    "requires_auth": False
                },
                "readiness": {
                    "method": "GET",
                    "path": "/ready",
                    "description": "서비스 준비 상태 확인",
                    "requires_auth": False
                },
                "liveness": {
                    "method": "GET",
                    "path": "/live",
                    "description": "서비스 생존 상태 확인",
                    "requires_auth": False
                }
            }
        }
    }
    
    return success_response(
        data=endpoints,
        message="API endpoints retrieved successfully"
    )


@router.get("/response-format")
async def get_response_format():
    """API 응답 형식 가이드"""
    
    response_formats = {
        "success_response": {
            "description": "성공 응답 형식",
            "structure": {
                "success": True,
                "message": "Success message",
                "timestamp": "2024-01-01T00:00:00.000000",
                "data": "Response data (optional)"
            }
        },
        "error_response": {
            "description": "에러 응답 형식",
            "structure": {
                "success": False,
                "message": "Error message",
                "timestamp": "2024-01-01T00:00:00.000000",
                "error_code": "ERROR_CODE (optional)",
                "details": "Additional error details (optional)"
            }
        },
        "paginated_response": {
            "description": "페이지네이션된 응답 형식",
            "structure": {
                "success": True,
                "message": "Success message",
                "timestamp": "2024-01-01T00:00:00.000000",
                "data": "Array of items",
                "meta": {
                    "page": "Current page number",
                    "limit": "Items per page",
                    "total": "Total items count",
                    "has_next": "Has next page",
                    "has_prev": "Has previous page",
                    "total_pages": "Total pages count"
                }
            }
        },
        "authentication": {
            "description": "인증이 필요한 API 호출 방법",
            "header": {
                "Authorization": "Bearer YOUR_JWT_TOKEN"
            },
            "example": "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
        "error_codes": {
            "USER_NOT_FOUND": "사용자를 찾을 수 없음",
            "SOCIAL_LOGIN_ERROR": "소셜 로그인 실패",
            "PROFILE_UPDATE_ERROR": "프로필 업데이트 실패",
            "FRIEND_ADD_ERROR": "친구 추가 실패",
            "FRIEND_REMOVE_ERROR": "친구 삭제 실패",
            "TOKEN_REFRESH_ERROR": "토큰 갱신 실패",
            "DEV_TOKEN_ERROR": "개발용 토큰 생성 실패"
        }
    }
    
    return success_response(
        data=response_formats,
        message="Response format guide retrieved successfully"
    )