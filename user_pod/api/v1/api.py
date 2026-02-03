from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, api_docs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(api_docs.router, prefix="/docs", tags=["api-documentation"])