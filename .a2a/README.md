# A2A (Agent-to-Agent) Communication Directory

This directory stores configurations and artifacts related to the Agent-to-Agent (A2A) communication protocol within the InstaBids platform.

## Contents

### `agent_cards/`

*   **Purpose**: Contains JSON files defining "agent cards" for each agent participating in the A2A network.
*   **Description**: An agent card acts as a public profile for an agent, describing its identity, capabilities, skills, and how other agents can authenticate and interact with it.
*   **Example**: `homeowner_agent.json` defines the card for the `HomeownerAgent`.
*   **Convention**: Each agent requiring A2A interaction should have its card defined here. Refer to Google ADK/A2A documentation for best practices on agent card fields.

### `events/`

*   **Purpose**: This directory is intended for A2A event-related artifacts. (Its specific use, e.g., for event schemas, examples, or logged event instances, should be further defined as the project evolves.)
*   **Note**: Core A2A event *definitions* (Python classes) are located in `src/instabids/a2a_comm/events.py`.

### `server_config.json`

*   **Purpose**: Likely contains configuration for the A2A communication server or bus.
*   **Description**: This could include details for service discovery, endpoint registration, or local A2A bus settings used during development and testing. The exact schema and usage will depend on the specific A2A framework implementation choices.

## A2A Protocol in InstaBids

All inter-agent communication in InstaBids is designed to adhere to the A2A protocol, facilitating decoupled and standardized interactions between different AI agents. The definitions for event types exchanged between agents are managed in `src/instabids/a2a_comm/events.py`.
