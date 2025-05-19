# ADK (Agent Development Kit) Directory

This directory is designated for configurations and resources specific to the Google Agent Development Kit (ADK) used in the InstaBids platform.

## Contents

### `models/`

*   **Purpose**: Intended for storing configurations or artifacts related to the Large Language Models (LLMs) or other machine learning models used by ADK agents.
*   **Description**: This could include specific model identifiers, fine-tuning configurations, prompt templates for ADK's internal use, or other model-related metadata that is globally relevant to ADK agents in this project.
*   **Note**: Agent-specific prompts are typically located within the respective agent's directory (e.g., `src/instabids/agents/homeowner/prompts.py`).

### `session_config.json`

*   **Purpose**: Contains configuration settings for ADK's session management.
*   **Description**: This file likely defines how agent sessions are persisted, including aspects like session storage type (e.g., in-memory, database), expiration policies, and other parameters that govern the lifecycle and statefulness of agent conversations and interactions.

### `tools/`

*   **Purpose**: This directory is reserved for ADK tool-related configurations or globally accessible tool schemas, if any.
*   **Description**: While primary agent tool *implementations* (Python classes) are located in `src/instabids/tools/`, this directory could house JSON schemas for tool inputs/outputs, configurations for externally hosted tools registered with ADK, or definitions for very generic tools used across multiple ADK agents if not placed within the main source package. The specific use should be defined as the project's tool architecture evolves.

## ADK in InstaBids

The Google Agent Development Kit (ADK) provides the core framework for building individual AI agents within InstaBids. It offers functionalities for agent lifecycle management, state persistence (sessions), tool integration, and interaction with LLMs. Agent implementations leveraging ADK are primarily located in `src/instabids/agents/`.
