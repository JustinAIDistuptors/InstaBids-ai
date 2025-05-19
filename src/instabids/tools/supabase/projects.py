# Supabase project-related tools

import logging
import uuid
from typing import Dict, Any, Optional

from google.adk.tools import Tool, ToolContext

logger = logging.getLogger(__name__)

class CreateProjectTool(Tool):
    """Tool to create a new project in Supabase."""

    name: str = "CreateProjectTool"
    description: str = "Creates a new project entry in the database."

    async def _invoke_async(
        self,
        tool_context: ToolContext,
        title: str,
        description: str,
        zipcode: str,
        budget_range: str,
        timeline: str,
        homeowner_id: Optional[str] = None, # Usually from tool_context.session.user_id
    ) -> Dict[str, str]:
        """Invokes the tool to create a project.

        Args:
            tool_context: The context in which the tool is invoked.
            title: The title of the project.
            description: The detailed description of the project.
            zipcode: The zipcode where the project is located.
            budget_range: The estimated budget for the project.
            timeline: The desired timeline for project completion.
            homeowner_id: The ID of the homeowner creating the project.

        Returns:
            A dictionary containing the ID of the newly created project.
        """
        actual_homeowner_id = homeowner_id or tool_context.session.user_id
        logger.info(
            f"Executing CreateProjectTool for homeowner_id: {actual_homeowner_id} with data: "
            f"Title: {title}, Description: {description[:50]}..., Zip: {zipcode}, "
            f"Budget: {budget_range}, Timeline: {timeline}"
        )
        # Mock implementation: In a real scenario, this would interact with Supabase.
        project_id = str(uuid.uuid4())
        logger.info(f"Mock CreateProjectTool: Created project with ID: {project_id}")
        # Simulate storing project data somewhere accessible if needed by other tools immediately,
        # or assume the caller (agent) handles state updates based on this ID.
        return {"project_id": project_id}

class UpdateProjectTool(Tool):
    """Tool to update an existing project in Supabase."""

    name: str = "UpdateProjectTool"
    description: str = "Updates an existing project entry in the database."

    async def _invoke_async(
        self,
        tool_context: ToolContext,
        project_id: str,
        update_data: Dict[str, Any],
    ) -> Dict[str, bool]:
        """Invokes the tool to update a project.

        Args:
            tool_context: The context in which the tool is invoked.
            project_id: The ID of the project to update.
            update_data: A dictionary containing the fields to update and their new values.

        Returns:
            A dictionary indicating whether the update was successful.
        """
        logger.info(
            f"Executing UpdateProjectTool for project_id: {project_id} with update_data: {update_data}"
        )
        # Mock implementation: In a real scenario, this would interact with Supabase.
        logger.info(f"Mock UpdateProjectTool: Updated project {project_id}")
        return {"success": True}

# To make them easily importable as modules for the agent's tools list
create_project_tool = CreateProjectTool()
update_project_tool = UpdateProjectTool()
