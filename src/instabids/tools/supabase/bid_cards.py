# Supabase bid card-related tools

import logging
import uuid
from typing import Dict, Any, Optional, List
import asyncio

from google.adk.tools import Tool, ToolContext
# Assuming a supabase_client module or similar for actual DB interaction
# from ....clients.supabase_client import SupabaseClient  # Example import

logger = logging.getLogger(__name__)

class CreateBidCardTool(Tool):
    """Tool to create a new bid card in Supabase."""

    name: str = "CreateBidCardTool"
    description: str = "Creates a new bid card entry in the database linked to a project with detailed classification."

    async def _invoke_async(
        self,
        tool_context: ToolContext,
        project_id: str,
        primary_category: str,
        primary_job_type: str,
        primary_ai_confidence: Optional[float] = None,
        secondary_category: Optional[str] = None,
        secondary_job_type: Optional[str] = None,
        secondary_ai_confidence: Optional[float] = None,
        tertiary_category: Optional[str] = None,
        tertiary_job_type: Optional[str] = None,
        tertiary_ai_confidence: Optional[float] = None,
        classification_details: Optional[Dict[str, Any]] = None,
        budget_range: Optional[str] = None,
        timeline: Optional[str] = None,
        photo_meta: Optional[List[Dict[str, Any]]] = None, # Updated to List
        status: str = "draft",
    ) -> Dict[str, Any]:
        """Invokes the tool to create a bid card.

        Args:
            tool_context: The context in which the tool is invoked. Contains clients like Supabase.
            project_id: The ID of the project this bid card belongs to.
            primary_category: The primary classified category of the project.
            primary_job_type: The primary classified job type of the project.
            primary_ai_confidence: AI confidence for the primary classification.
            secondary_category: Secondary classified category.
            secondary_job_type: Secondary classified job type.
            secondary_ai_confidence: AI confidence for secondary classification.
            tertiary_category: Tertiary classified category.
            tertiary_job_type: Tertiary classified job type.
            tertiary_ai_confidence: AI confidence for tertiary classification.
            classification_details: Raw output or reasoning from the classifier.
            budget_range: The estimated budget for the project.
            timeline: The desired timeline for project completion.
            photo_meta: Metadata from vision analysis of project photos (list of dicts).
            status: The initial status of the bid card (e.g., 'draft', 'final').

        Returns:
            A dictionary containing the details of the newly created bid card or an error.
        """
        logger.info(
            f"Executing CreateBidCardTool for project_id: {project_id} with data: "
            f"Primary Category: {primary_category}, Primary Job Type: {primary_job_type}, "
            f"Primary Confidence: {primary_ai_confidence}, Budget: {budget_range}, "
            f"Timeline: {timeline}, Status: {status}"
        )
        if secondary_category:
            logger.info(f"Secondary: {secondary_category}/{secondary_job_type} ({secondary_ai_confidence})")
        if tertiary_category:
            logger.info(f"Tertiary: {tertiary_category}/{tertiary_job_type} ({tertiary_ai_confidence})")
        if photo_meta:
            logger.info(f"{len(photo_meta)} photo metadata entries included.")
        if classification_details:
            logger.info(f"Classification details included: {list(classification_details.keys())}")

        supabase_client = tool_context.clients.get("supabase") # Assuming Supabase client is in tool_context.clients
        if not supabase_client:
            logger.error("Supabase client not found in ToolContext. Cannot create bid card.")
            return {"error": "Supabase client not configured", "details": "Client not found in ToolContext."}

        bid_card_data_to_insert = {
            "project_id": project_id,
            "primary_category": primary_category,
            "primary_job_type": primary_job_type,
            "primary_ai_confidence": primary_ai_confidence,
            "secondary_category": secondary_category,
            "secondary_job_type": secondary_job_type,
            "secondary_ai_confidence": secondary_ai_confidence,
            "tertiary_category": tertiary_category,
            "tertiary_job_type": tertiary_job_type,
            "tertiary_ai_confidence": tertiary_ai_confidence,
            "classification_details": classification_details or {},
            "budget_range": budget_range,
            "timeline": timeline,
            "photo_meta": photo_meta or [],
            "status": status,
            # 'id' and 'inserted_at', 'updated_at' will be handled by the database (default or trigger)
        }

        try:
            logger.info(f"Attempting to insert bid card data: {bid_card_data_to_insert}")
            # Actual Supabase call
            # response = await supabase_client.table('bid_cards').insert(bid_card_data_to_insert).execute()
            # For now, using a sync equivalent for the call structure as an example
            # The actual call might be `await supabase_client.rpc(...)` or `await supabase_client.from_('bid_cards').insert(...).execute()`
            # This needs to be verified with the actual Supabase Python client library used in the project.
            
            # Placeholder for actual Supabase call structure
            # Assuming a response structure that contains data or an error
            # For example, if using PostgREST directly or a client that mimics it:
            # result = await supabase_client.from_("bid_cards").insert(bid_card_data_to_insert).execute()

            # Simulating a successful insertion for now, as the exact Supabase client API is unknown.
            # In a real scenario, you would get the inserted row back, including its 'id' and 'created_at'.
            
            # MOCKING THE SUCCESSFUL DB INTERACTION FOR NOW
            # Replace this block with actual Supabase client call and error handling
            # START MOCK
            await asyncio.sleep(0.1) # Simulate async network call
            mock_inserted_id = str(uuid.uuid4())
            created_bid_card_from_db = {
                **bid_card_data_to_insert, 
                "id": mock_inserted_id, 
                "inserted_at": "mock_timestamp_from_db", 
                "updated_at": "mock_timestamp_from_db"
            }
            logger.info(f"Successfully created bid card with ID: {mock_inserted_id} in database (mocked).")
            # END MOCK
            
            # if result.error:
            #     logger.error(f"Error creating bid card in Supabase: {result.error.message}")
            #     return {"error": "Failed to create bid card", "details": result.error.message}
            # else:
            #     created_bid_card_from_db = result.data[0] if result.data else None
            #     if not created_bid_card_from_db:
            #         logger.error("Failed to create bid card: No data returned from Supabase after insert.")
            #         return {"error": "Failed to create bid card", "details": "No data returned after insert."}
            #     logger.info(f"Successfully created bid card with ID: {created_bid_card_from_db.get('id')} in database.")
            return created_bid_card_from_db

        except Exception as e:
            logger.exception(f"Exception occurred while creating bid card for project {project_id}: {e}")
            return {"error": "Exception during bid card creation", "details": str(e)}

# To make it easily importable
create_bid_card_tool = CreateBidCardTool()
