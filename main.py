from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.connector_helper import spec_router
from app.api.api_v1.api import api_router
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings, logger

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Starting falcon-connector app")
logger.info("Exposing /metrics endpoint for metrics scrapping")

Instrumentator().instrument(app).expose(app)
app.include_router(spec_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Hello World"}
