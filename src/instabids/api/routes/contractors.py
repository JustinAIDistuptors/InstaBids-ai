"""Contractor API routes."""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_contractors():
    return [{"id": "contractor1", "name": "Placeholder Contractor Inc."}]
