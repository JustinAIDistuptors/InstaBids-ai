"""
Projects API routes for InstaBids.

This module defines the API routes for project-related operations.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from ..dependencies import get_runner, get_supabase
from ..middlewares.auth import get_current_user
from ...sessions.session_service import get_session_service
from google.genai.types import Content, Part

logger = logging.getLogger(__name__)

router = APIRouter()


class ProjectCreate(BaseModel):
    """Schema for project creation request."""
    title: Optional[str] = Field(None, description="Project title")
    description: str = Field(..., description="Project description")
    zipcode: Optional[str] = Field(None, description="Project zipcode")
    budget_range: Optional[str] = Field(None, description="Budget range")
    timeline: Optional[str] = Field(None, description="Project timeline")


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: str
    owner_id: str
    title: str
    description: str
    zipcode: str
    status: str
    inserted_at: str # Assuming Supabase provides this


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_project_route(
    project_data: Optional[ProjectCreate] = None, # Changed to optional to allow Form data priority
    image: Optional[UploadFile] = File(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    zipcode: Optional[str] = Form(None),
    budget_range: Optional[str] = Form(None),
    timeline: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user),
    runner = Depends(get_runner),
    session_service = Depends(get_session_service),
):
    """
    Create a new project and optionally upload an image.
    
    This endpoint accepts either JSON data or form data with an optional image.
    It triggers the HomeownerAgent to process the project information and
    generate a bid card.
    """
    try:
        current_description = ""
        current_title = None

        if project_data and project_data.description:
            current_description = project_data.description
            current_title = project_data.title
        elif description:
            current_description = description
            current_title = title
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project description is required either in JSON body or form data."
            )

        # Prepare initial slots from either ProjectCreate or Form data
        initial_slots = {}
        if project_data:
            initial_slots = {k: v for k, v in project_data.dict().items() if v is not None}
        
        # Form data can override or provide values if project_data is not fully provided
        if title is not None: initial_slots['title'] = title
        if description is not None: initial_slots['description'] = description
        if zipcode is not None: initial_slots['zipcode'] = zipcode
        if budget_range is not None: initial_slots['budget_range'] = budget_range
        if timeline is not None: initial_slots['timeline'] = timeline
        
        import uuid
        session_id = str(uuid.uuid4())
        
        session = session_service.get_or_create_session(
            app_name="instabids",
            user_id=user_id,
            session_id=session_id
        )
        
        session.state["slots"] = initial_slots
        
        if image:
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            # Sanitize filename if necessary, though UploadFile.filename should be okay
            image_filename = image.filename if image.filename else "uploaded_image"
            image_path = os.path.join(temp_dir, f"{session_id}_{image_filename}")
            
            with open(image_path, "wb") as buffer:
                buffer.write(await image.read())
            
            session.state["image_path"] = image_path
            logger.info(f"Image saved to: {image_path}")
        
        # Construct user message for the agent
        # The HomeownerAgent's _run_async_impl expects to pick up 'slots' and 'image_path' from session.state
        # The initial message text can be simple, or constructed to kick off the agent's logic if needed.
        # Based on HomeownerAgent, it will try to fill slots. If description is present, it's a good start.
        agent_kickoff_message = initial_slots.get("description", "New project creation attempt.")
        if initial_slots.get("title"):
            agent_kickoff_message = f"{initial_slots['title']}: {agent_kickoff_message}"

        content = Content(
            role="user",
            parts=[Part(text=agent_kickoff_message)]
        )
        
        final_event = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                final_event = event
                break
        
        project_id_from_state = session.state.get("project_id")
        bid_card_id_from_state = session.state.get("bid_card_id")
        
        if not project_id_from_state:
            logger.error(f"Project ID not found in session state after agent run. Session: {session_id}, State: {session.state}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project or retrieve project ID from agent."
            )
        
        response_payload = {
            "project_id": project_id_from_state,
            "bid_card_id": bid_card_id_from_state,
            "session_id": session_id,
        }
        
        if final_event and final_event.content and final_event.content.parts:
            response_payload["agent_message"] = final_event.content.parts[0].text
        
        return response_payload
    
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.exception(f"Error creating project via route: {e}") # Use logger.exception for stack trace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    """
    Get a project by ID.
    
    Only the project owner can access their projects due to RLS policies.
    """
    try:
        if supabase is None:
             raise HTTPException(status_code=503, detail="Database service not available")
        response = await supabase.table("projects").select("*").eq("id", project_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project = response.data[0]
        
        # RLS should enforce this, but defensive check is good.
        if project["owner_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
        
        return project
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = Depends(get_current_user),
    supabase = Depends(get_supabase),
):
    """
    List all projects for the current user.
    
    Returns only the user's own projects due to RLS policies.
    """
    try:
        if supabase is None:
             raise HTTPException(status_code=503, detail="Database service not available")
        response = await supabase.table("projects").select("*").eq("owner_id", user_id).execute()
        return response.data
    
    except Exception as e:
        logger.exception(f"Error listing projects for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
