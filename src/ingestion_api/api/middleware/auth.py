from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.ingestion_api.config import settings

class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
            
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != settings.API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API Key"})
            
        return await call_next(request)
