"""API dependencies.

Common dependencies used across API routes.
"""
from fastapi import Request, HTTPException, status

async def get_runner(request: Request):
    if not hasattr(request.app.state, 'runner') or not request.app.state.runner:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADK Runner not initialized."
        )
    return request.app.state.runner

async def get_supabase(request: Request):
    # Placeholder for Supabase client dependency
    # In a real app, you'd initialize Supabase client (e.g., in main.py startup)
    # and make it available, perhaps via app.state or another mechanism.
    # For now, returning a mock or None.
    print("WARNING: get_supabase is a placeholder and does not return a real Supabase client.")
    # Example: return request.app.state.supabase_client
    return None
