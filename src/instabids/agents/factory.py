"""Agent factory for creating agent instances."""
from .homeowner.agent import HomeownerAgent
# Import other agents here as they are created
# from .outbound_recruiter.agent import OutboundRecruiterAgent

_agents = {
    "homeowner": HomeownerAgent,
    # "outbound_recruiter": OutboundRecruiterAgent,
}

def get_agent(agent_name: str):
    agent_class = _agents.get(agent_name.lower())
    if not agent_class:
        raise ValueError(f"Agent '{agent_name}' not found.")
    # You might pass configurations or other dependencies here if needed
    return agent_class()
