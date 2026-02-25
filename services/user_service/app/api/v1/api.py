from fastapi import APIRouter
from app.api.routes import users, friends, upload, challenges, cat_images, cat_character, cat_character_test

api_router = APIRouter()

# 라우터 포함
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(cat_images.router, prefix="/cats", tags=["cat-images"])
api_router.include_router(cat_character.router, prefix="/cat-character", tags=["cat-character"])
api_router.include_router(cat_character_test.router, prefix="/cat-character-test", tags=["cat-character-test"])