# AI-Specific Directory

This directory houses files and configurations that are specific to the Artificial Intelligence (AI) aspects of the InstaBids platform, particularly those relating to agent development, behavior, and project management.

## Contents

### `changelog.jsonl`

*   **Purpose**: Tracks significant development progress and changes related to AI components and agents.
*   **Format**: Each entry is a JSON object on a new line (JSON Lines format) and should adhere to the following schema:
    *   `timestamp` (string, ISO 8601): Time of the change.
    *   `type` (string): Type of change (e.g., "feature", "fix", "refactor", "docs").
    *   `component` (string): The agent or module affected (e.g., "homeowner_agent", "bidcard_module").
    *   `description` (string): A brief summary of the change.
    *   `changes` (array of strings): List of file paths modified.
    *   `status` (string): Current status (e.g., "completed", "in_progress", "planned").
*   **Usage**: This log is updated (simulated in AI assistant responses during development) to maintain a record of AI-related development activities.

### `components.json`

*   **Purpose**: Intended to define or describe the various AI components within the InstaBids system.
*   **Description**: This file could serve as a manifest, listing AI agents, modules, or services, potentially including their versions, dependencies, or high-level capabilities. Its exact structure and usage should be standardized as the project evolves. *(Placeholder for future definition)*

### `context.json`

*   **Purpose**: Designed to store global contextual information that might be relevant to multiple AI agents or the AI system as a whole.
*   **Description**: This could include shared knowledge snippets, domain-specific terminology, global operational parameters for AI, or environment-specific settings that influence AI behavior. The schema should be defined based on identified needs. *(Placeholder for future definition)*

### `conventions.json`

*   **Purpose**: Intended to document specific conventions related to AI development within InstaBids.
*   **Description**: This might include prompt engineering guidelines, data formatting rules for AI inputs/outputs, preferred styles for AI-generated content, or other AI-specific coding or design conventions not covered in the main `AI_README.md`. *(Placeholder for future definition)*

## AI Development in InstaBids

The primary guide for AI development practices, architectural decisions, and detailed agent patterns is the `AI_README.md` located in the project root. This `.ai/` directory serves to hold specific configuration files and metadata supporting those development efforts.
