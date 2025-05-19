"""
HomeownerAgent implementation for InstaBids.

This agent handles homeowner interactions, project scoping, and bid card generation.
It uses slot-filling to collect necessary project information and delegates to the
BidCardModule for classification and bid card creation.
"""

from typing import Dict, List, Optional, Any, AsyncGenerator
import logging
from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from ...tools.supabase.projects import create_project, update_project
from ...tools.supabase.preferences import get_user_preference, set_user_preference
from ...tools.vision.image_analysis import analyze_image
from ..bidcard.generator import generate_bid_card
from .prompts import SYSTEM_PROMPT, SLOT_FILLING_PROMPT

logger = logging.getLogger(__name__)


class HomeownerAgent(LlmAgent):
    """
    Agent that interacts with homeowners to scope projects and generate bid cards.
    
    This agent uses a conversational slot-filling approach to gather necessary
    project information from the homeowner. It can recall user preferences from
    previous interactions and delegates to the BidCardModule for project
    classification and bid card generation.
    """
    
    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        name: str = "HomeownerAgent",
        description: str = "Helps homeowners scope projects and generates bid cards",
    ):
        """
        Initialize the HomeownerAgent.
        
        Args:
            model: The model to use for the agent (default: gemini-2.0-flash)
            name: The name of the agent (default: HomeownerAgent)
            description: A description of the agent's purpose
        """
        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=SYSTEM_PROMPT,
            tools=[
                create_project,
                update_project,
                get_user_preference,
                set_user_preference,
                analyze_image,
            ],
            output_key="project_info"
        )
        self.required_slots = [
            "title",
            "description",
            "zipcode",
            "budget_range",
            "timeline",
        ]
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implement the agent's core logic.
        
        This method orchestrates the slot-filling process, preference management,
        and bid card generation. It yields events as the conversation progresses.
        
        Args:
            ctx: The invocation context containing session and state information
            
        Yields:
            Events representing the agent's processing and responses
        """
        # Initialize slots with any existing project information
        slots = ctx.session.state.get("slots", {})
        
        # If an image was uploaded, analyze it
        if "image_path" in ctx.session.state:
            image_path = ctx.session.state["image_path"]
            logger.info(f"Analyzing image: {image_path}")
            
            # Call vision tool to analyze the image
            image_analysis_result = await self._analyze_image(ctx, image_path)
            
            # Update state with image analysis results
            ctx.session.state["photo_meta"] = image_analysis_result
            
            # Log the analysis result
            logger.info(f"Image analysis complete: {image_analysis_result}")
        
        # Look up user preferences if we don't have all required slots
        if not self._all_slots_filled(slots):
            logger.info("Not all slots filled, retrieving user preferences")
            await self._load_user_preferences(ctx, slots)
        
        # Main conversation loop for slot-filling
        while not self._all_slots_filled(slots):
            # Prepare slot-filling prompt based on current slots
            next_prompt = self._prepare_slot_filling_prompt(slots)
            
            # Get user's response
            user_message = await self._get_user_message(ctx) # This method needs to be defined or imported
            
            # Extract information from user message and update slots
            # This method also needs to be defined or the logic implemented here
            updated_slots = await self._extract_slots_from_message(ctx, user_message, slots) 
            slots.update(updated_slots)
            
            # Store any extracted preferences
            if "budget_range" in updated_slots and updated_slots["budget_range"]:
                await self._store_user_preference(
                    ctx, "default_budget", updated_slots["budget_range"], 0.8
                )
            
            # Update session state with current slots
            ctx.session.state["slots"] = slots
            
            # Yield updated state to ensure persistence
            yield Event(
                author=self.name,
                actions=Event.Actions(state_delta={"slots": slots})
            )
            
            # If still missing slots, ask for more information
            if not self._all_slots_filled(slots):
                response = f"I need a bit more information to complete your project. {next_prompt}"
                yield Event.for_text(self.name, response)
        
        # All slots filled, create the project
        logger.info(f"All slots filled: {slots}")
        project_id = await self._create_project(ctx, slots)
        
        # Generate bid card
        if project_id:
            bid_card = await self._generate_bid_card(ctx, project_id, slots)
            
            # Update session state with completed project and bid card info
            ctx.session.state["project_id"] = project_id
            ctx.session.state["bid_card_id"] = bid_card["id"]
            
            # Yield updated state
            yield Event(
                author=self.name,
                actions=Event.Actions(
                    state_delta={
                        "project_id": project_id,
                        "bid_card_id": bid_card["id"]
                    }
                )
            )
            
            # Prepare final response with bid card details
            confidence_level = "high" if bid_card["ai_confidence"] >= 0.7 else "moderate"
            final_response = (
                f"Great! I've created your project and generated a bid card. "
                f"Your project has been classified as a {bid_card['category']} > {bid_card['job_type']} "
                f"with {confidence_level} confidence. "
                f"Once you confirm the details look good, I'll help find contractors for your {bid_card['category']} project."
            )
            
            # Return final response
            yield Event.for_text(self.name, final_response)
    
    def _all_slots_filled(self, slots: Dict[str, Any]) -> bool:
        """Check if all required slots are filled."""
        return all(slot in slots and slots[slot] for slot in self.required_slots)
    
    def _prepare_slot_filling_prompt(self, slots: Dict[str, Any]) -> str:
        """Prepare the next prompt based on missing slots."""
        missing_slots = [slot for slot in self.required_slots if slot not in slots or not slots[slot]]
        
        if "title" in missing_slots:
            return "What's a good title for your project?"
        elif "description" in missing_slots:
            return "Please describe your project in detail. What specifically needs to be done?"
        elif "zipcode" in missing_slots:
            return "What's the zipcode where the project will take place?"
        elif "budget_range" in missing_slots:
            return "What's your budget range for this project?"
        elif "timeline" in missing_slots:
            return "When would you like this project to be completed?"
        
        return "Is there anything else you'd like to add about your project?"

    async def _get_user_message(self, ctx: InvocationContext) -> str:
        """Placeholder for getting user message. ADK likely provides a way to get the last user utterance."""
        # This needs to be implemented based on how ADK provides user input
        # For now, returning a placeholder or raising NotImplementedError
        if ctx.history and ctx.history[-1].author == "user":
             return ctx.history[-1].text
        logger.warning("_get_user_message needs proper implementation based on ADK context.")
        return "Placeholder user message - replace with actual user input mechanism."

    async def _extract_slots_from_message(self, ctx: InvocationContext, user_message: str, current_slots: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for extracting slots from user message using LLM or regex."""
        # This method needs to be implemented. It might involve another LLM call
        # or specific parsing logic based on expected user responses.
        # For now, it's a placeholder.
        logger.warning("_extract_slots_from_message needs proper implementation.")
        extracted_slots = {}
        # Example (very naive) - a real implementation would use LLM or robust parsing
        if "title" not in current_slots or not current_slots["title"]:
            # In a real scenario, you'd use an LLM call with a specific prompt
            # to extract the title from user_message
            pass # Placeholder
        # ... and so on for other slots
        return extracted_slots
    
    async def _load_user_preferences(self, ctx: InvocationContext, slots: Dict[str, Any]):
        """Load user preferences and update slots with defaults if available."""
        try:
            user_id = ctx.session.user_id
            if not user_id:
                logger.warning("User ID not found in session, cannot load preferences.")
                return
            
            budget_preference = await get_user_preference(
                user_id=user_id,
                preference_key="default_budget",
                tool_context=ToolContext(
                    state=ctx.session.state,
                    agent_name=self.name,
                    function_call_id="load_preferences"
                )
            )
            
            if budget_preference and "budget_range" not in slots:
                slots["budget_range"] = budget_preference
                logger.info(f"Loaded default budget preference: {budget_preference}")
        
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
    
    async def _store_user_preference(
        self, ctx: InvocationContext, key: str, value: Any, confidence: float
    ):
        """Store a user preference with confidence score."""
        try:
            user_id = ctx.session.user_id
            if not user_id:
                logger.warning("User ID not found in session, cannot store preference.")
                return
            
            await set_user_preference(
                user_id=user_id,
                preference_key=key,
                preference_value=value,
                confidence=confidence,
                tool_context=ToolContext(
                    state=ctx.session.state,
                    agent_name=self.name,
                    function_call_id="store_preference"
                )
            )
            
            logger.info(f"Stored user preference: {key}={value} (confidence={confidence})")
        
        except Exception as e:
            logger.error(f"Error storing user preference: {e}")
    
    async def _analyze_image(self, ctx: InvocationContext, image_path: str) -> Dict[str, Any]:
        """Analyze an uploaded image using the vision tool."""
        try:
            result = await analyze_image(
                image_path=image_path,
                tool_context=ToolContext(
                    state=ctx.session.state,
                    agent_name=self.name,
                    function_call_id="analyze_image"
                )
            )
            return result
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"error": str(e)}
    
    async def _create_project(self, ctx: InvocationContext, slots: Dict[str, Any]) -> Optional[str]:
        """Create a project in the database using filled slots."""
        try:
            user_id = ctx.session.user_id
            if not user_id:
                logger.error("User ID not found in session, cannot create project.")
                return None
            
            result = await create_project(
                owner_id=user_id,
                title=slots["title"],
                description=slots["description"],
                zipcode=slots["zipcode"],
                status="scoping",
                tool_context=ToolContext(
                    state=ctx.session.state,
                    agent_name=self.name,
                    function_call_id="create_project"
                )
            )
            
            logger.info(f"Created project: {result}")
            return result["id"]
        
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    async def _generate_bid_card(
        self, ctx: InvocationContext, project_id: str, slots: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a bid card for the project using the BidCardModule."""
        try:
            photo_meta = ctx.session.state.get("photo_meta", {})
            
            bid_card = await generate_bid_card(
                project_id=project_id,
                project_data=slots,
                photo_meta=photo_meta
            )
            
            logger.info(f"Generated bid card: {bid_card}")
            return bid_card
        
        except Exception as e:
            logger.error(f"Error generating bid card: {e}")
            return {
                "id": "error",
                "project_id": project_id,
                "category": "unknown",
                "job_type": "unknown",
                "ai_confidence": 0.0,
                "status": "draft"
            }