import logging

from fastapi import FastAPI

from app.core.container import close_resources, init_resources
from app.routes.health import router as health_router
from app.routes.vision import router as vision_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="vision-validate-service", version="1.0.0")
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(vision_router, tags=["vision"])


@app.on_event("startup")
def startup() -> None:
    init_resources()


@app.on_event("shutdown")
def shutdown() -> None:
    close_resources()
