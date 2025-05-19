# Supabase bid card-related tools

import logging
import uuid
from typing import Dict, Any, Optional

from google.adk.tools import Tool, ToolContext

logger = logging.getLogger(__name__)

class CreateBidCardTool(Tool):
    """Tool to create a new bid card in Supabase."""

    name: str = "CreateBidCardTool"
    description: str = "Creates a new bid card entry in the database linked to a project."

    async def _invoke_async(
        self,
        tool_context: ToolContext,
        project_id: str,
        category: str,
        job_type: str,
        budget_range: Optional[str] = None,
        timeline: Optional[str] = None,
        photo_meta: Optional[Dict[str, Any]] = None,
        ai_confidence: Optional[float] = None,
        status: str = "draft",
    ) -> Dict[str, Any]:
        """Invokes the tool to create a bid card.

        Args:
            tool_context: The context in which the tool is invoked.
            project_id: The ID of the project this bid card belongs to.
            category: The classified category of the project.
            job_type: The classified job type of the project.
            budget_range: The estimated budget for the project.
            timeline: The desired timeline for project completion.
            photo_meta: Metadata from vision analysis of project photos.
            ai_confidence: The AI's confidence score in the classification.
            status: The initial status of the bid card (e.g., 'draft', 'final').

        Returns:
            A dictionary containing the details of the newly created bid card.
        """
        logger.info(
            f"Executing CreateBidCardTool for project_id: {project_id} with data: "
            f"Category: {category}, Job Type: {job_type}, Budget: {budget_range}, "
            f"Timeline: {timeline}, AI Confidence: {ai_confidence}, Status: {status}"
        )
        if photo_meta:
            logger.info(f"Photo metadata included: {list(photo_meta.keys())}")

        # Mock implementation
        bid_card_id = str(uuid.uuid4())
        created_bid_card = {
            "id": bid_card_id,
            "project_id": project_id,
            "category": category,
            "job_type": job_type,
            "budget_range": budget_range,
            "timeline": timeline,
            "photo_meta": photo_meta or {},
            "ai_confidence": ai_confidence,
            "status": status,
            "created_at": "mock_timestamp", # In real scenario, use current timestamp
        }
        logger.info(f"Mock CreateBidCardTool: Created bid card with ID: {bid_card_id} -> {created_bid_card}")
        return created_bid_card

# To make it easily importable
create_bid_card_tool = CreateBidCardTool()
