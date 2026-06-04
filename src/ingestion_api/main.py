from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uuid

from src.ingestion_api.config import settings
from src.ingestion_api.api.routes import telemetry, suppliers, schemas, health
from src.ingestion_api.api.middleware.auth import APIKeyAuthMiddleware
from src.ingestion_api.kafka_producer.producer import producer

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    producer.flush()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(APIKeyAuthMiddleware)

@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(health.router, tags=["health"])
app.include_router(telemetry.router, prefix=f"{settings.API_V1_STR}/telemetry", tags=["telemetry"])
app.include_router(suppliers.router, prefix=f"{settings.API_V1_STR}/suppliers", tags=["suppliers"])
app.include_router(schemas.router, prefix=f"{settings.API_V1_STR}/schemas", tags=["schemas"])
