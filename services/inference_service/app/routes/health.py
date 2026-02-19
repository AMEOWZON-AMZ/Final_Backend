from fastapi import APIRouter

router = APIRouter()


# 서비스 가동 상태를 확인하는 헬스체크 엔드포인트.
@router.get("/")
async def health():
    return {"status": "ok"}
