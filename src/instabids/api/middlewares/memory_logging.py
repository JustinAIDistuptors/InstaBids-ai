"""Memory logging middleware."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class MemoryLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Placeholder: Implement actual memory logging
        # print(f"Request to: {request.url.path}")
        response = await call_next(request)
        # print(f"Response status: {response.status_code}")
        return response
