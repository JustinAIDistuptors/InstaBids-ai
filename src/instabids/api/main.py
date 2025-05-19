"""
Main FastAPI application for InstaBids.

This module sets up the FastAPI application with all routes, middleware,
and dependencies. It also configures the A2A server for agent communication.
"""

import logging
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from .middlewares.auth import get_current_user # Placeholder needed
from .middlewares.memory_logging import MemoryLoggingMiddleware # Placeholder needed
from .routes import projects, messages, contractors # Placeholders for messages & contractors routes needed
from ..sessions.session_service import get_session_service # Placeholder needed
from ..sessions.memory_service import get_memory_service # Placeholder needed
from ..agents.factory import get_agent # Placeholder needed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="InstaBids API",
    description="API for InstaBids multi-agent bidding platform",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add memory logging middleware
app.add_middleware(MemoryLoggingMiddleware)

# Include routers
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(contractors.router, prefix="/contractors", tags=["contractors"])

# Initialize services and agents
@app.on_event("startup")
async def startup_event():
    """Initialize services and agents on startup."""
    logger.info("Starting InstaBids API")
    
    session_service = get_session_service()
    logger.info("Session service initialized")
    
    memory_service = get_memory_service()
    logger.info("Memory service initialized")
    
    homeowner_agent = get_agent("homeowner")
    # Assuming Runner is part of ADK and configured correctly
    # The runner setup might need adjustment based on actual ADK usage
    runner = Runner(
        agent=homeowner_agent, 
        app_name="instabids", 
        session_service=session_service, 
        memory_service=memory_service
    )
    app.state.runner = runner # Storing runner in app state
    logger.info("Agents initialized and registered")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "InstaBids API"}

@app.get("/system-info")
async def system_info():
    """Return system information for diagnostics."""
    return {
        "agents": [
            {"name": "HomeownerAgent", "status": "active"},
            {"name": "OutboundRecruiterAgent", "status": "pending"}, # Assuming this agent will be added
        ],
        "services": [
            {"name": "SessionService", "status": "active"},
            {"name": "MemoryService", "status": "active"},
        ],
    }