# InstaBids A2A Documentation

This document describes the Agent-to-Agent (A2A) specific implementation details for the InstaBids platform.

## A2A Protocol Overview

The InstaBids platform uses the Google A2A protocol to facilitate communication between different agent types:
- HomeownerAgent: Interacts with homeowners to collect project details
- OutboundRecruiterAgent: Reaches out to contractors based on project needs
- ContractorAgent: Represents contractors in the bidding process

## Agent Card Definitions

Agent cards in `.a2a/agent_cards/` define each agent's capabilities, authentication requirements, and supported interaction modes.

## A2A Server Configuration

The A2A server implementation in this repository follows Google's reference implementation with:
- TaskManager pattern for handling agent requests
- Server-Sent Events (SSE) for real-time streaming updates
- JWT authentication for secure agent-to-agent communication

## Event Definitions

The `.a2a/events/` directory contains JSON schema definitions for all events exchanged between agents, including project creation, bid submission, and communication events.

## Recommended Implementation Approach

When implementing A2A functionality:
1. Start with defining agent cards
2. Implement the TaskManager for specific agent types
3. Connect the SSE streaming endpoints
4. Test agent-to-agent communications via the A2A protocol

## Integration with ADK

ADK agents can utilize A2A functionality through a client interface. See the `ADK_README.md` for more details on this integration.
