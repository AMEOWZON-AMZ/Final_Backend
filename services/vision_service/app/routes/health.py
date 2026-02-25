from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health() -> dict[str, bool]:
    return {"ok": True}
