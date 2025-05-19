# InstaBids - Multi-Agent Bidding Platform

> Connect homeowners with contractors through AI-assisted project scoping and bidding

## Overview

InstaBids is a multi-agent system leveraging Google's Agent Development Kit (ADK) and Agent-to-Agent (A2A) protocol to streamline home improvement projects from creation to bidding. It uses AI agents to assist homeowners in scoping projects, automatically reach out to contractors, and facilitate bidding and communication – all integrated with a modern web frontend and robust backend services.

## Why InstaBids Exists

Homeowners hate chasing quotes; contractors hate vague leads.
Our platform proves that a small team of cooperating AI agents can:

1. **Understand a project from one photo or short chat**,
2. **Generate a structured Bid Card automatically**, and
3. **Invite the right local contractors** in minutes.

## User Journey (Happy Path)
Photo/Voice ➜ HomeownerAgent (chat) ➜ BidCardModule ➜ ⚡ Confirm ➜ OutboundRecruiterAgent ➜ Contractor Accepts ➜ MatchMade event ➜ Chat opens

1. **Capture** – Homeowner drops a picture or voice note in the Next.js app.
2. **Scope** – `HomeownerAgent` (Gemini + tools) asks follow‑ups until all required slots are filled.
3. **Bid Card** – `BidCardModule` writes a `bid_cards` row in Supabase.
4. **Confirm** – Agent shows card; homeowner taps **Looks good**.
5. **Match** – `OutboundRecruiterAgent` queries the `contractors` table, emails/SMS invites.
6. **Connect** – First contractor to click **Interested** triggers **MatchMade**; chat unblinds contacts.

## Agent Architecture

InstaBids uses a multi-agent architecture based on Google ADK and A2A:

| Agent/Module           | Description                                                          | Status       |
| ---------------------- | -------------------------------------------------------------------- | ------------ |
| HomeownerAgent         | Conversational slot-filling, preference recall, bid card generation  | Implemented  |
| BidCardModule          | Classify project, enrich with photo_meta, create Bid Card JSON       | Implemented  |
| OutboundRecruiterAgent | Select & invite contractors, fire MatchMade                          | In Progress  |
| MessagingBroker        | Store & stream chat, mask PII until match                            | Implemented  |

All cross-agent traffic uses **A2A events** in `a2a_comm/events.py`.

## Tech Stack

| Layer           | Choice                       | Why                                        |
| --------------- | ---------------------------- | ------------------------------------------ |
| LLM             | **Gemini Pro** via Vertex AI | Native in Google ADK, vision ready         |
| Vision          | Gemini Vision API            | Single call → labels + bounding boxes      |
| Agent Framework | **Google ADK 0.6** + **A2A** | First-class event bus & tracing            |
| Backend         | FastAPI + Uvicorn            | Async prompts, simple OpenAPI docs         |
| Frontend        | Next.js 14 + shadcn/ui       | Rapid SSR + React hooks                    |
| DB              | Supabase Postgres            | Row-Level Security + Realtime channels     |
| CI              | GitHub Actions               | pytest + Cypress + Supabase test container |

## Local Dev Quick-Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- pnpm (run `npm install -g pnpm` if needed)
- Docker and Docker Compose (for local Supabase)

### Setup

```bash
# clone
$ git clone https://github.com/instabids/mvp.git && cd mvp

# env vars
$ cp .env.example .env   # add GOOGLE_API_KEY, SUPABASE_SERVICE_ROLE_KEY, etc.

# start stack
$ docker-compose up -d   # Postgres + studio on :54323
# $ pnpm install && pnpm dev # Next.js on :3000 # Assuming frontend dir exists and has package.json

# In a new terminal (for the backend API if not run by docker-compose directly for dev)
# If your docker-compose 'api' service runs the backend, this might not be needed separately.
# $ uvicorn src.instabids.api.main:app --reload --port 8000 

# For frontend (if not managed by docker-compose for dev):
# cd frontend 
# pnpm install && pnpm dev 

```
Open http://localhost:3000 (if frontend is running), create a user account, then upload a test image or start a chat to create a project.

## Environment Variables
Required environment variables (typically in a `.env` file at the project root for local development, and as secrets for CI/CD):

- `GOOGLE_API_KEY`: Google API key for Gemini Pro and other Google Cloud services.
- `SUPABASE_URL`: URL for your Supabase project (e.g., `http://localhost:54321` for local Docker, or your cloud Supabase URL).
- `SUPABASE_ANON_KEY`: Anon key for frontend Supabase client.
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for backend Supabase client (provides admin-like access).
- `OPENAI_API_KEY` (Optional): OpenAI API key if using OpenAI models for vision analysis or other tasks.
- `ALLOWED_ORIGINS` (For FastAPI CORS): Comma-separated list of allowed origins (e.g., `http://localhost:3000` for the frontend).

## Testing

- **Unit/Integration (Python)**: `pytest -v tests/unit tests/integration` (uses test Supabase from CI or local setup).
- **E2E (Frontend/Cypress)**: `cd frontend && pnpm run cypress:run` (runs headless browser flow against a running application stack).

CI (GitHub Actions) must pass before merging to `main`.

## Repository Structure

This repository follows an architecture optimized for AI agent-driven development:

```
instabids/
├── .a2a/                  # A2A-specific configurations (e.g., agent cards)
├── .github/               # GitHub Actions workflows (CI/CD)
├── .vscode/               # VSCode settings (optional)
├── db/
│   └── migrations/        # Supabase/PostgreSQL migration files
├── frontend/              # Next.js frontend application (assumed)
├── src/
│   └── instabids/         # Main Python package for the backend
│       ├── a2a_comm/      # A2A event definitions and communication logic
│       ├── agents/        # Agent implementations (Homeowner, OutboundRecruiter, etc.)
│       │   ├── homeowner/
│       │   └── ...
│       ├── api/           # FastAPI application (main.py, routes, dependencies, middleware)
│       │   ├── routes/
│       │   └── middlewares/
│       ├── sessions/      # Session and memory management services (ADK)
│       ├── tools/         # Tool implementations for agents (if any custom)
│       └── utils/         # Common utility functions
├── tests/
│   ├── unit/              # Unit tests for Python backend
│   └── integration/       # Integration tests for Python backend
├── .dockerignore          # Specifies files to ignore in Docker builds
├── .env.example           # Example environment variables file
├── .gitignore             # Specifies intentionally untracked files that Git should ignore
├── AI_README.md           # Specific guidelines for AI development in this project
├── Dockerfile             # Dockerfile for the Python backend API
├── docker-compose.yml     # Docker Compose for local development environment
├── README.md              # This file: project overview, setup, etc.
├── requirements.txt       # Python dependencies for the backend
└── supabase_config/       # Placeholder for Supabase specific configs like kong.yaml (if needed)
```

## Documentation

- API Documentation (auto-generated by FastAPI at `/docs` and `/redoc` on the running API)
- Agent Architecture (see sections in this README and `AI_README.md`)
- Database Schema (see SQL files in `db/migrations/`)
- Contributing Guide (`CONTRIBUTING.md` - to be created)

## Contributing

See `CONTRIBUTING.md` for detailed contribution guidelines (once created).

The short version:

- Branch `feature/<slug>` or `fix/<slug>` from `main`.
- Ensure CI passes (linting, tests).
- Format code: Python (Black + Flake8), Frontend (ESLint + Prettier).
- New agents must ship with an A2A JSON card and relevant tests.
- PRs should be reviewed before merging.
