# AI Development Guidelines for InstaBids

## Project Overview
- Project: InstaBids Multi-Agent Bidding Platform
- Purpose: Connect homeowners with contractors through AI-assisted project scoping and bidding
- Status: MVP Development
- Primary stakeholders: Homeowners, Contractors

## Agent Architecture
InstaBids uses a multi-agent architecture based on Google ADK and A2A:

1. **HomeownerAgent**: Handles homeowner interactions, project scoping, and bid card generation
2. **BidCardModule**: Processes and classifies projects, generates structured bid cards
3. **OutboundRecruiterAgent**: Matches contractors to projects and sends invitations
4. **MessagingBroker**: Manages communication between parties

## Development Workflows

### Feature Implementation Process
1. Review specifications in `specs/[feature_area]`
2. Identify affected components in `.ai/components.json`
3. Follow established patterns in `docs/patterns.md`
4. Implement in the appropriate module directory
5. Add tests following the patterns in `tests/`
6. Update `.ai/changelog.jsonl`

### Agent Enhancement Process
1. Analyze current agent behavior in `agents/[agent_name]/`
2. Review prompts in `agents/[agent_name]/prompts.py`
3. Make surgical modifications to prompts or agent logic
4. Test agent behavior with various inputs
5. Add regression tests that verify the enhancement
6. Document changes in ADRs if substantive

## Code Style Guidelines
- Follow PEP 8 for Python code
- Use type hints for all function parameters and return values
- Document all public methods with docstrings
- For frontend, follow Airbnb JavaScript Style Guide
- Use functional React components and hooks

## Agent Implementation Guidelines
- Keep agents focused on single responsibilities
- Use the `ToolContext` for accessing session state and memory
- Implement before_tool and before_model callbacks for guardrails
- Structure prompts clearly with examples for complex tasks
- Use the A2A protocol for inter-agent communication

## A2A Communication Standards
- Define all events in `a2a_comm/events.py`
- Ensure events include proper validation
- Tag events with correlation IDs for tracing
- Add proper documentation to all event classes

## Database Interaction Guidelines
- Use Supabase tools for all database operations
- Apply Row-Level Security (RLS) policies for user data
- Use service role key only when necessary
- Document all table schemas and relationships

## Testing Requirements
- Each agent must have unit tests for its core functionality
- Integration tests must verify end-to-end workflows
- Test fixtures should be reusable and well-documented
- Run the full test suite before submitting changes

## Memory and State Management
- Use the Session service for user preferences
- Document any state keys you introduce
- Clean up temporary state after use
- Use proper namespacing for state keys

## Vision Processing Guidelines
- Handle image analysis asynchronously
- Store analysis results in the photo_meta field
- Implement proper error handling for vision processing
- Consider privacy implications of image data

## Security Guidelines
- Never expose API keys in client-side code
- Validate all user inputs server-side
- Use parameterized queries for database operations
- Apply proper authentication checks in API routes

## Project-Specific Considerations
- Budget ranges should follow predefined tiers
- Location data should be validated with geo services
- Photo metadata should be sanitized before storage
- Agent tone should be professional but conversational