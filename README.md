# AFK Slackbot

A FastAPI-based Slack app to manage and broadcast "AFK" (away-from-keyboard) status updates in your Slack workspace. Team members can quickly set AFK windows with a natural-language phrase using the `/afk` slash command, list current AFKs, view a monospace table, or clear their status. Records are stored in MongoDB and messages are posted via Slack Block Kit.

## Features
- **/afk <phrase>**: Parse a natural-language time range (e.g., `for 1 hour`, `until 5pm`, `from 2pm to 3:30pm`). If parsing fails, the bot opens an interactive modal to pick start/end.
- **/afk list**: Shows active AFK entries for the workspace.
- **/afk table**: Shows a monospace table of active AFKs.
- **/afk clear**: Cancels your currently active AFK records.
- **Persistence**: Stores AFK records in MongoDB using Motor (async PyMongo).
- **Locale-aware display**: Uses user locale and timezone to render times.

## Architecture
- API server: FastAPI (`main.py`)
  - `POST /v1/slack_bot`: Slash command endpoint (form encoded) handling create/list/table/clear.
  - `POST /v1/interactive_message`: Slack interactivity endpoint for the manual date-time submission flow.
  - `GET /health-check`: Health endpoint.
- Core modules (`lib/`)
  - `models.py`: Pydantic models (AFKRecord, AFKRecordFilter, SlackPostRequestBody, UserInfo) and enums.
  - `command_handlers.py`: Subcommand handlers and Slack message flow.
  - `services/`:
    - `mongo_db.py`: Initializes Motor client and exposes `afk_records_collection`.
    - `database_service.py`: CRUD on AFK records and AFK clearing logic.
    - `slack_service.py`: Slack WebClient integration and Block Kit builders.
  - `utils.py`: Helpers (MongoDB filter builder, formatting for display, etc.).

## Requirements
- Python 3.14+ (3.14 supported for local dev tooling)
- MongoDB (local or hosted)
- A Slack app with a bot token and the correct scopes

## Environment variables
Provide these via `.env` (or your hosting provider’s secret manager). The app also reads `/etc/secrets/.env` when present (e.g., on some hosts).

Required:
- `SLACK_BOT_TOKEN` — Bot token beginning with `xoxb-...`
- `SLACK_SIGNING_SECRET` — Slack signing secret for request verification
- `MONGODB_URI` — MongoDB connection string (e.g., `mongodb://localhost:27017`)
- `PORT` — Port for the FastAPI server (defaults to 8000 if unset)
- `ENABLE_HOT_RELOAD` — `true` to enable Uvicorn reload in dev, otherwise `false`

Example `.env`:
```
SLACK_BOT_TOKEN=xoxb-***
SLACK_SIGNING_SECRET=***
MONGODB_URI=mongodb://localhost:27017
PORT=8000
ENABLE_HOT_RELOAD=true
```

## Install and run locally
Use the provided `Makefile` to create a virtualenv and install dependencies.

1) Create venv and install dev deps:
```
make install_dev
```

2) Start MongoDB (local or Docker). For local Mongo: ensure it runs on `mongodb://localhost:27017` or set `MONGODB_URI` accordingly.

3) Run the app:
```
make run
```
The server will start on `http://localhost:8000`. Visit `http://localhost:8000/health-check` to verify.

Notes:
- Slack request verification in `main.py` uses `slack_sdk.signature.SignatureVerifier` but is currently commented out. For production, enable it by uncommenting those lines to validate `X-Slack-Signature` and `X-Slack-Request-Timestamp`.

## Slack app setup
You can import `manifest.json` to speed up Slack app configuration.

Scopes (bot):
- `chat:write`, `chat:write.customize`, `chat:write.public`, `commands`, `users:read`, `channels:join`

Slash command:
- Command: `/afk`
- Request URL: `https://<your-host>/v1/slack_bot`
- Short description: Manage AFK status
- Usage hint: for an hour

Interactivity:
- Enable interactivity
- Request URL: `https://<your-host>/v1/interactive_message`

Install the app to your workspace and copy:
- Bot token → `SLACK_BOT_TOKEN`
- Signing secret → `SLACK_SIGNING_SECRET`

## Using the bot
In any channel where the bot is present:
- `/afk for an hour` — Creates an AFK record for the next hour and posts a message.
- `/afk until 5pm` or `/afk from 2pm to 3:30pm` — Natural language parsing via `afk_parser`.
- If parsing fails, an interactive date-time picker is sent.
- `/afk list` — Shows active AFK entries.
- `/afk table` — Shows a monospace table.
- `/afk clear` — Cancels your active AFK entries.

## Testing
Integration tests cover the database service with a real MongoDB in Docker.

Prerequisites:
- Docker and Docker Compose installed

Run the test suite:
```
make test
```
This will:
- Build a test image from `Dockerfile.test` (Python 3.14, installs dev requirements)
- Start MongoDB container and the tester container using `docker-compose-test.yaml`
- Execute `pytest -vv`

Cleanup containers and network:
```
make cleanup
```
Remove the tester image (deep cleanup):
```
make cleanup_deep
```

## Deployment notes
- The repo includes a simple `vercel.json` pointing at `main.py`. For production use on Vercel or any other host, ensure:
  - `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, and `MONGODB_URI` are configured as environment variables.
  - Public HTTPS URLs are set in Slack for slash command and interactivity.
- When hosting elsewhere (e.g., Render, Fly.io, Docker on a VPS), expose port `${PORT}` and configure the same environment variables. The app will also load `/etc/secrets/.env` if available.

## Project layout
- `main.py` — FastAPI app and HTTP routes
- `lib/models.py` — Pydantic models and enums
- `lib/command_handlers.py` — Command handlers and Slack message flow
- `lib/services/mongo_db.py` — Mongo client and collection
- `lib/services/database_service.py` — Mongo CRUD and AFK clearing
- `lib/services/slack_service.py` — Slack Web API and Block Kit builders
- `lib/utils.py` — Utilities (formatting, query building)
- `tests/` — Pytest suite for database service
- `manifest.json` — Slack app manifest (import into Slack)
- `Makefile` — Dev tasks (install, test, lint, format)
