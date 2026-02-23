from fastapi import APIRouter
from app.api.routes import users, friends, upload, challenges

api_router = APIRouter()

# 라우터 포함
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])