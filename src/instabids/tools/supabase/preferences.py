# Supabase user preference-related tools

import logging
from typing import Dict, Any, Optional

from google.adk.tools import Tool, ToolContext

logger = logging.getLogger(__name__)

class GetUserPreferenceTool(Tool):
    """Tool to retrieve a user preference from Supabase."""

    name: str = "GetUserPreferenceTool"
    description: str = "Retrieves a specific user preference from the database."

    async def _invoke_async(
        self,
        tool_context: ToolContext,
        preference_key: str,
        user_id: Optional[str] = None, # Usually from tool_context.session.user_id
    ) -> Dict[str, Any]:
        """Invokes the tool to get a user preference.

        Args:
            tool_context: The context in which the tool is invoked.
            preference_key: The key of the preference to retrieve.
            user_id: The ID of the user whose preference is being retrieved.

        Returns:
            A dictionary containing the preference key and its value, or None if not found.
        """
        actual_user_id = user_id or tool_context.session.user_id
        logger.info(
            f"Executing GetUserPreferenceTool for user_id: {actual_user_id}, preference_key: {preference_key}"
        )
        # Mock implementation
        mock_preferences = {
            "default_budget": "$500-$1000",
            "preferred_contact_method": "email"
        }
        value = mock_preferences.get(preference_key)
        logger.info(f"Mock GetUserPreferenceTool: Retrieved {preference_key} = {value}")
        return {"preference_key": preference_key, "value": value}

class SetUserPreferenceTool(Tool):
    """Tool to set a user preference in Supabase."""

    name: str = "SetUserPreferenceTool"
    description: str = "Sets or updates a specific user preference in the database."

    async def _invoke_async(
        self,
        tool_context: ToolContext,
        preference_key: str,
        preference_value: Any,
        user_id: Optional[str] = None, # Usually from tool_context.session.user_id
    ) -> Dict[str, bool]:
        """Invokes the tool to set a user preference.

        Args:
            tool_context: The context in which the tool is invoked.
            preference_key: The key of the preference to set.
            preference_value: The value of the preference.
            user_id: The ID of the user whose preference is being set.

        Returns:
            A dictionary indicating whether the preference was set successfully.
        """
        actual_user_id = user_id or tool_context.session.user_id
        logger.info(
            f"Executing SetUserPreferenceTool for user_id: {actual_user_id}, "
            f"preference_key: {preference_key}, value: {preference_value}"
        )
        # Mock implementation
        logger.info(f"Mock SetUserPreferenceTool: Set {preference_key} = {preference_value}")
        return {"success": True}

# To make them easily importable as modules for the agent's tools list
get_user_preference_tool = GetUserPreferenceTool()
set_user_preference_tool = SetUserPreferenceTool()
