"""
Homeowner Agent for InstaBids.

This agent interacts with homeowners to gather project details, manage preferences,
and orchestrate the creation of projects and bid cards using various ADK tools.
"""
import logging
from typing import Dict, Any, AsyncGenerator, Optional, List

from google.adk.agents import LlmAgent, InvocationContext, Tool, Event
import google.generativeai.types as glm # For ToolCall and ToolResult

from .prompts import SYSTEM_PROMPT, SLOT_FILLING_PROMPT, BUDGET_EXTRACTION_PROMPT
from .tools import ( # Assuming tools are correctly defined and imported
    create_project_tool,
    update_project_tool,
    get_user_preference_tool,
    set_user_preference_tool,
    analyze_image_tool,
    create_bid_card_tool,
)
from instabids.agents.bidcard.generator import generate_bid_card_data # Corrected import path

logger = logging.getLogger(__name__)

class HomeownerAgent(LlmAgent):
    def __init__(self, **kwargs):
        super().__init__(
            tools=[
                create_project_tool,
                update_project_tool,
                get_user_preference_tool,
                set_user_preference_tool,
                analyze_image_tool,
                create_bid_card_tool,
            ],
            **kwargs,
        )
        # Create a mapping from tool names to tool instances for easy lookup
        self._tools_by_name: Dict[str, Tool] = {tool.name: tool for tool in self.tools}
        logger.info(f"HomeownerAgent initialized with tools: {list(self._tools_by_name.keys())}")

        self.agent_states = {
            "GREETING": 0,
            "LOADING_PREFERENCES": 1,
            "ANALYZING_IMAGE": 2,
            "SLOT_FILLING": 3,
            "CREATING_PROJECT": 4,
            "GENERATING_BID_CARD_DATA": 5,
            "CREATING_BID_CARD": 6,
            "COMPLETED": 7,
            "ERROR": 8,
        }

    def _get_current_state_name(self, ctx: InvocationContext) -> str:
        state_value = ctx.session.state.get("agent_internal_state", self.agent_states["GREETING"])
        for name, val in self.agent_states.items():
            if val == state_value:
                return name
        return "UNKNOWN_STATE"

    def _extract_tool_calls_from_llm_response(
        self, response: glm.GenerateContentResponse
    ) -> List[glm.ToolCall]:
        """Extracts tool calls from the LLM's response."""
        tool_calls = []
        if response and response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if isinstance(part, glm.ToolCall):
                            tool_calls.append(part)
        return tool_calls

    def _extract_text_from_llm_response(
        self, response: glm.GenerateContentResponse
    ) -> Optional[str]:
        """Extracts the primary text content from the LLM's response."""
        if response and response.text:
            return response.text
        # Fallback if text is not directly available but might be in parts
        if response and response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
                    if text_parts:
                        return " ".join(text_parts).strip()
        return None

    async def _execute_tool_call(
        self, ctx: InvocationContext, tool_call: glm.ToolCall
    ) -> glm.ToolResult:
        """Executes a single tool call and returns its result."""
        tool_name = tool_call.function_call.name
        tool_args = dict(tool_call.function_call.args)
        tool_output_content = ""
        error_occurred = False

        if tool_name not in self._tools_by_name:
            tool_output_content = f"Error: Tool '{tool_name}' not found or not registered with the agent."
            logger.error(tool_output_content)
            error_occurred = True
        else:
            actual_tool: Tool = self._tools_by_name[tool_name]
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
            try:
                # Assuming tools have an 'arun' method for async execution
                # and they return a dictionary or a serializable object.
                tool_output_python = await actual_tool.arun(ctx, **tool_args) 
                
                # Process direct output and update state HERE
                slots = ctx.session.state.get("slots", {})
                self._handle_tool_output_and_update_state(ctx, tool_name, tool_output_python, slots)

                # ADK expects the 'output' for ToolResult to be a string.
                # We need to decide how to represent complex Python outputs.
                # For now, let's assume a simple string conversion or a summary.
                # This part is CRITICAL and depends on what the LLM expects back.
                if isinstance(tool_output_python, dict):
                    tool_output_content = str(tool_output_python) # Simple string representation
                elif isinstance(tool_output_python, str):
                    tool_output_content = tool_output_python
                else:
                    tool_output_content = f"Tool {tool_name} executed successfully (output type: {type(tool_output_python)})."
                
                logger.info(f"Tool {tool_name} executed. Raw Python output: {tool_output_python}")

            except Exception as e:
                tool_output_content = f"Error executing tool '{tool_name}': {str(e)}"
                logger.exception(f"Exception while executing tool {tool_name}:")
                error_occurred = True
                ctx.session.state["agent_internal_state"] = self.agent_states["ERROR"]
        
        return glm.ToolResult(
            part=glm.Part(function_response=glm.FunctionResponse(name=tool_name, response={"content": tool_output_content, "error": error_occurred})),
            role="tool" # ADK might expect role='tool'
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        logger.info(f"HomeownerAgent _run_async_impl triggered. Invocation ID: {ctx.invocation_id}")
        
        # Initialize session state if not present
        if "slots" not in ctx.session.state:
            ctx.session.state["slots"] = {}
        if "agent_internal_state" not in ctx.session.state:
            ctx.session.state["agent_internal_state"] = self.agent_states["GREETING"]
        if "user_id" not in ctx.session.state: # Assuming user_id is set externally or via a login flow
            ctx.session.state["user_id"] = "default_user_123" # Placeholder
            logger.warning("user_id not found in session, using placeholder.")

        slots = ctx.session.state["slots"]
        current_state_value = ctx.session.state["agent_internal_state"]
        current_state_name = self._get_current_state_name(ctx)

        logger.info(f"Current agent state: {current_state_name} ({current_state_value})")
        logger.info(f"Current slots: {slots}")
        logger.info(f"User input for this turn: {ctx.get_last_user_message()}")

        # --- Main Agent Logic based on State ---
        if current_state_value == self.agent_states["ERROR"]:
            yield Event(author=self.name, content="I seem to have encountered an issue. Could you please try rephrasing or starting over?", invocation_id=ctx.invocation_id)
            ctx.end_invocation = True
            return

        if current_state_value == self.agent_states["COMPLETED"]:
            yield Event(author=self.name, content="Project and bid card creation process is complete. What would you like to do next?", invocation_id=ctx.invocation_id)
            ctx.end_invocation = True # Or transition to another state
            return

        # Construct conversation history for the LLM
        # This needs to be built from ctx.history or similar ADK mechanism
        # For now, let's build a simplified history
        conversation_history = [glm.Content(parts=[glm.Part(text=SYSTEM_PROMPT)], role="system")] # System prompt first
        # Add previous turns from ADK's history if available
        # For example: for turn in ctx.history: conversation_history.append(turn)
        # Then add current user message
        last_user_message = ctx.get_last_user_message()
        if last_user_message:
            conversation_history.append(glm.Content(parts=[glm.Part(text=last_user_message)], role="user"))
        else: # First turn, no user message yet (e.g. agent starts convo)
            if current_state_value == self.agent_states["GREETING"]:
                 conversation_history.append(glm.Content(parts=[glm.Part(text="Initiate greeting.")], role="user")) # Simulate trigger

        # Add specific prompt based on state if needed (e.g. SLOT_FILLING_PROMPT)
        if current_state_value == self.agent_states["SLOT_FILLING"]:
            # The SLOT_FILLING_PROMPT is now part of SYSTEM_PROMPT's guidance
            # but could be added here if more specific turn-based instruction is needed.
            pass 

        # --- LLM Interaction --- 
        logger.debug(f"Sending content to LLM. History length: {len(conversation_history)}")
        llm_response: glm.GenerateContentResponse = await ctx.llm.generate_content_async(
            contents=conversation_history,
            # tools=self.tools, # ADK's LlmAgent might handle this internally if tools are in __init__
            # tool_config=glm.ToolConfig(...) # If specific tool config needed
        )

        tool_calls_requested = self._extract_tool_calls_from_llm_response(llm_response)
        final_text_response_to_user = self._extract_text_from_llm_response(llm_response)

        if tool_calls_requested:
            logger.info(f"LLM requested {len(tool_calls_requested)} tool call(s).")
            tool_results: List[glm.ToolResult] = []
            for tool_call in tool_calls_requested:
                tool_execution_result = await self._execute_tool_call(ctx, tool_call)
                tool_results.append(tool_execution_result)
            
            # Update conversation history with the LLM's previous request and our tool results
            conversation_history.append(llm_response.candidates[0].content) # Add LLM's turn that requested tools
            conversation_history.append(glm.Content(parts=tool_results, role="tool")) # Add all tool results

            logger.debug(f"Sending tool results back to LLM. History length: {len(conversation_history)}")
            final_llm_response: glm.GenerateContentResponse = await ctx.llm.generate_content_async(
                contents=conversation_history
            )
            final_text_response_to_user = self._extract_text_from_llm_response(final_llm_response)
            if final_text_response_to_user:
                logger.info(f"LLM response after tool execution: {final_text_response_to_user[:100]}...")
            else:
                logger.warning("LLM provided no text response after tool execution.")
                final_text_response_to_user = "I've processed that using my tools. What's next?" # Fallback
        else:
            if final_text_response_to_user:
                logger.info(f"LLM response (no tools called): {final_text_response_to_user[:100]}...")
            else:
                logger.warning("LLM provided no text response and no tools were called.")
                final_text_response_to_user = "I'm sorry, I didn't quite understand. Could you rephrase?" # Fallback

        # --- Update Agent State based on LLM response and current state ---
        # This logic needs to be robust. The LLM (guided by prompts) and tool outputs should drive state changes.
        # For now, a simplified state update based on slots and current state.
        
        # Example state transition logic (needs to be more sophisticated)
        if current_state_value == self.agent_states["GREETING"]:
            ctx.session.state["agent_internal_state"] = self.agent_states["SLOT_FILLING"] 
            # Potentially LOADING_PREFERENCES or ANALYZING_IMAGE if conditions met
            if ctx.session.state.get("user_id") and not slots.get("budget_range"):
                 # Prompt implies GetUserPreferenceTool might be used by LLM here
                 pass 
            if ctx.session.state.get("image_path") and not ctx.session.state.get("photo_meta"):
                # Prompt implies AnalyzeImageTool might be used by LLM here
                pass
        
        elif current_state_value == self.agent_states["SLOT_FILLING"]:
            if self._all_slots_filled(slots):
                # LLM should confirm before this state transition implicitly happens.
                # The SYSTEM_PROMPT instructs LLM to confirm before CreateProjectTool.
                # This agent state transition should occur *after* LLM confirms and requests CreateProjectTool.
                # For now, we assume if LLM doesn't ask more questions and slots are full, it's time for project creation.
                # A more robust way is for LLM to output a specific signal or the CreateProjectTool call itself signals this transition.
                # If 'project_id' is now in state (from CreateProjectTool via _handle_tool_output_and_update_state):
                if ctx.session.state.get("project_id"):
                    ctx.session.state["agent_internal_state"] = self.agent_states["GENERATING_BID_CARD_DATA"]
                else: # Slots are filled, but project not yet created. LLM should be prompting to create it.
                    logger.info("All slots filled, expecting LLM to confirm and request project creation.")
        
        elif current_state_value == self.agent_states["GENERATING_BID_CARD_DATA"]:
            project_id = ctx.session.state.get("project_id")
            if project_id:
                project_data_for_bid_card = { # Gather data for generate_bid_card_data
                    "title": slots.get("title"),
                    "description": slots.get("description"),
                    "zip_code": slots.get("zipcode"), # Ensure key matches generate_bid_card_data expectation
                    "budget_range": slots.get("budget_range"),
                    "timeline": slots.get("timeline"),
                    "owner_id": ctx.session.state.get("user_id")
                }
                photo_meta = ctx.session.state.get("photo_meta")
                try:
                    bid_card_params = await generate_bid_card_data(project_id, project_data_for_bid_card, photo_meta)
                    ctx.session.state["bid_card_params"] = bid_card_params
                    ctx.session.state["agent_internal_state"] = self.agent_states["CREATING_BID_CARD"]
                    logger.info("Bid card data generated, transitioning to CREATING_BID_CARD state.")
                    # The LLM should now be prompted to use CreateBidCardTool with these params
                    # We might need to re-engage LLM here to inform it that bid_card_params are ready.
                    # For now, we assume next turn's SYSTEM_PROMPT/context will guide it.
                    final_text_response_to_user = "I've prepared the details for the bid card. Let's get that created." # Override LLM text for this transition
                except Exception as e:
                    logger.exception("Error calling generate_bid_card_data:")
                    ctx.session.state["agent_internal_state"] = self.agent_states["ERROR"]
                    final_text_response_to_user = "I encountered an issue preparing the bid card data."
            else:
                logger.error("In GENERATING_BID_CARD_DATA state but no project_id found.")
                ctx.session.state["agent_internal_state"] = self.agent_states["ERROR"]

        elif current_state_value == self.agent_states["CREATING_BID_CARD"]:
            # LLM should be guided by SYSTEM_PROMPT to use CreateBidCardTool if bid_card_params are available.
            # If 'bid_card_id' is now in state (from CreateBidCardTool via _handle_tool_output_and_update_state):
            if ctx.session.state.get("bid_card_id"):
                ctx.session.state["agent_internal_state"] = self.agent_states["COMPLETED"]
                logger.info("Bid card created, transitioning to COMPLETED state.")
            else:
                logger.info("Waiting for LLM to use CreateBidCardTool or for tool result.")

        # Yield the final text response to the user.
        yield Event(author=self.name, content=final_text_response_to_user, invocation_id=ctx.invocation_id)
        logger.info(f"Yielding event with content: {final_text_response_to_user[:100]}...")
        logger.info(f"Next agent state: {self._get_current_state_name(ctx)}")

    def _handle_tool_output_and_update_state(
        self, ctx: InvocationContext, tool_name: str, tool_output: Any, slots: Dict[str, Any]
    ):
        """
        Processes the direct Python output from a tool call and updates session state.
        This is called immediately after a tool's `arun` method completes.
        """
        logger.info(f"Handling output from tool '{tool_name}'. Output: {str(tool_output)[:200]}...")

        if tool_name == get_user_preference_tool.name:
            if isinstance(tool_output, dict) and tool_output.get("preference_key") == "default_budget" and tool_output.get("value"):
                if not slots.get("budget_range"):
                    slots["budget_range"] = tool_output["value"]
                    logger.info(f"Applied preference from GetUserPreferenceTool: budget_range set to {slots['budget_range']}")
                    ctx.session.state["slots"] = slots
        
        elif tool_name == analyze_image_tool.name:
            ctx.session.state["photo_meta"] = tool_output
            logger.info(f"Image analysis result from AnalyzeImageTool processed and stored in photo_meta.")

        elif tool_name == create_project_tool.name:
            project_id = tool_output.get("project_id") if isinstance(tool_output, dict) else None
            if project_id:
                ctx.session.state["project_id"] = project_id
                logger.info(f"Project creation result from CreateProjectTool processed. Project ID: {project_id}")
                # State transition to GENERATING_BID_CARD_DATA might happen in main loop after LLM confirms
            else:
                logger.error(f"CreateProjectTool output did not contain a 'project_id'. Output: {tool_output}")
                ctx.session.state["agent_internal_state"] = self.agent_states["ERROR"]

        elif tool_name == create_bid_card_tool.name:
            bid_card_id = tool_output.get("bid_card_id") if isinstance(tool_output, dict) else None
            if bid_card_id:
                ctx.session.state["bid_card_id"] = bid_card_id
                logger.info(f"Bid card creation result from CreateBidCardTool processed. Bid Card ID: {bid_card_id}")
                # State transition to COMPLETED might happen in main loop after LLM confirms
            else:
                logger.error(f"CreateBidCardTool output did not contain a 'bid_card_id'. Output: {tool_output}")
                ctx.session.state["agent_internal_state"] = self.agent_states["ERROR"]
        
        elif tool_name == set_user_preference_tool.name:
            logger.info(f"SetUserPreferenceTool was called and executed. Output: {tool_output}")
            # Confirmation to user is handled by LLM based on prompts.

        elif tool_name == update_project_tool.name:
            logger.info(f"UpdateProjectTool was called and executed. Output: {tool_output}")
            # Specific state updates for update_project would go here if needed.

        else:
            logger.warning(f"Received output from an unhandled tool in _handle_tool_output_and_update_state: {tool_name}")


    def _all_slots_filled(self, slots: Dict[str, Any]) -> bool:
        """Checks if all required slots are filled."""
        required_slots = ["title", "description", "zipcode", "budget_range", "timeline"]
        for slot_name in required_slots:
            if not slots.get(slot_name):
                logger.debug(f"Slot '{slot_name}' is not filled.")
                return False
        logger.info("All required slots are filled.")
        return True

    async def _get_budget_from_text(self, ctx: InvocationContext, text: str) -> Optional[str]:
        """Uses LLM to extract budget range from text if direct extraction fails."""
        # This method might be simplified or removed if the main LLM handles budget extraction well.
        prompt = BUDGET_EXTRACTION_PROMPT.format(text_to_analyze=text)
        logger.info("Attempting to extract budget using BUDGET_EXTRACTION_PROMPT.")
        
        response = await ctx.llm.generate_content_async(contents=[glm.Content(parts=[glm.Part(text=prompt)], role="user")])
        extracted_budget = self._extract_text_from_llm_response(response)
        
        if extracted_budget and "none" not in extracted_budget.lower(): # Basic check
            logger.info(f"Budget extracted via LLM: {extracted_budget}")
            return extracted_budget
        logger.warning("Could not extract budget using BUDGET_EXTRACTION_PROMPT.")
        return None