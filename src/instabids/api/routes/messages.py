"""Message API routes."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_messages():
    return [{"id": "msg1", "content": "Hello from messages placeholder!"}]
