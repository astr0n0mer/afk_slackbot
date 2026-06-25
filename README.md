# AFK Slackbot

A FastAPI Slack app for managing away-from-keyboard status updates in a Slack workspace. Team members use the `/afk` slash command to set AFK windows with natural-language phrases, list active AFKs, view a compact table, or clear their own status. Records are stored in MongoDB and responses are posted with Slack Block Kit.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Install and Run Locally](#install-and-run-locally)
- [Slack App Setup](#slack-app-setup)
- [Using the Bot](#using-the-bot)
- [Development Commands](#development-commands)
- [Testing](#testing)
- [Deployment Notes](#deployment-notes)
- [Project Layout](#project-layout)
- [Suggested Improvements](#suggested-improvements)

## Features

- `/afk <phrase>` parses natural-language time ranges such as `for 1 hour`, `until 5pm`, or `from 2pm to 3:30pm`.
- `/afk list` shows active AFK entries for the workspace.
- `/afk table` shows active AFK entries in a monospace table.
- `/afk clear` cancels the current user's active AFK entries.
- Interactive fallback opens a Slack date-time picker when the phrase cannot be parsed.
- MongoDB persistence stores AFK records with Motor, the async PyMongo driver.
- Locale-aware display uses Slack user locale and timezone data when rendering times.

## Architecture

- API server: `main.py`
  - `POST /v1/slack_bot`: slash command endpoint for create, list, table, and clear flows.
  - `POST /v1/interactive_message`: Slack interactivity endpoint for manual date-time submission.
  - `GET /health-check`: health endpoint.
- Core modules: `lib/`
  - `models.py`: Pydantic models and enums.
  - `command_handlers.py`: subcommand handlers and Slack response flow.
  - `services/mongo_db.py`: Motor client initialization and collection wiring.
  - `services/database_service.py`: AFK record CRUD and clear logic.
  - `services/slack_service.py`: Slack Web API calls and Block Kit builders.
  - `utils.py`: formatting, MongoDB filter construction, and shared helpers.

## Requirements

- Python 3.14+
- `uv`
- MongoDB, local or hosted
- Docker and Docker Compose for the containerized integration test flow
- A Slack app with a bot token and slash command support

## Configuration

Provide configuration through `.env` for local development, or through your hosting provider's secret manager in production. The app also loads `/etc/secrets/.env` when present.

Required variables:

| Variable | Description |
| --- | --- |
| `SLACK_BOT_TOKEN` | Slack bot token beginning with `xoxb-...`. |
| `SLACK_SIGNING_SECRET` | Slack signing secret used to verify incoming requests. |
| `MONGODB_URI` | MongoDB connection string, for example `mongodb://localhost:27017`. |
| `PORT` | HTTP port for the FastAPI server. Defaults to `8000`. |
| `ENABLE_HOT_RELOAD` | Set to `true` to enable Uvicorn reload in development. |

Example `.env`:

```dotenv
SLACK_BOT_TOKEN=xoxb-***
SLACK_SIGNING_SECRET=***
MONGODB_URI=mongodb://localhost:27017
PORT=8000
ENABLE_HOT_RELOAD=true
```

## Install and Run Locally

Install dependencies with `uv`:

```sh
make install_dev
```

Start MongoDB locally, or point `MONGODB_URI` at a hosted database. For a default local setup, use:

```dotenv
MONGODB_URI=mongodb://localhost:27017
```

Run the app:

```sh
make run
```

The server starts on `http://localhost:8000` by default. Check `http://localhost:8000/health-check` to confirm it is running.

Security note: Slack request verification is currently present in `main.py` but commented out. Enable it before production use so incoming requests are validated with `X-Slack-Signature` and `X-Slack-Request-Timestamp`.

## Slack App Setup

Import `manifest.json` in Slack to speed up app configuration.

Bot scopes:

- `chat:write`
- `chat:write.customize`
- `chat:write.public`
- `commands`
- `users:read`
- `channels:join`

Slash command:

- Command: `/afk`
- Request URL: `https://<your-host>/v1/slack_bot`
- Short description: `Manage AFK status`
- Usage hint: `for an hour`

Interactivity:

- Enable interactivity.
- Request URL: `https://<your-host>/v1/interactive_message`

After installing the app to your workspace, copy the bot token to `SLACK_BOT_TOKEN` and the signing secret to `SLACK_SIGNING_SECRET`.

## Using the Bot

Use these commands in any channel where the bot is present:

```text
/afk for an hour
/afk until 5pm
/afk from 2pm to 3:30pm
/afk list
/afk table
/afk clear
```

If the bot cannot parse the requested time range, it sends an interactive date-time picker.

## Development Commands

The Makefile uses `uv` for Python dependency management and command execution.

| Command | Description |
| --- | --- |
| `make install` | Install production dependencies. |
| `make install_dev` | Install runtime and development dependencies. |
| `make run` | Run the FastAPI app with `uv run`. |
| `make lint` | Run Pyright. |
| `make format` | Format Python files with Ruff. |
| `make test_local` | Run pytest against the currently configured MongoDB. |
| `make test` | Run the Docker Compose integration test stack with Python 3.14. |
| `make cleanup` | Stop and remove the Docker Compose test stack. |
| `make cleanup_deep` | Remove the test stack and tester image. |
| `make upgrade_dependencies` | Upgrade dependencies through `uv sync --upgrade`. |

## Testing

Integration tests cover the database service with a real MongoDB container.

Run the containerized test suite:

```sh
make test
```

This builds `Dockerfile.test`, starts MongoDB from `docker-compose-test.yaml`, and runs:

```sh
uv run pytest tests -v
```

Clean up containers and networks:

```sh
make cleanup
```

Remove the tester image as well:

```sh
make cleanup_deep
```

If MongoDB is already available through `MONGODB_URI`, run local tests with:

```sh
make test_local
```

To run local tests with a specific Python version:

```sh
make test_local TEST_PYTHON=3.14
```

## Deployment Notes

The repo includes `vercel.json` pointing at `main.py`. For Vercel or another host:

- Configure `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, and `MONGODB_URI` as environment variables.
- Set public HTTPS Slack request URLs for slash commands and interactivity.
- Expose `${PORT}` when deploying outside Vercel.
- Ensure Slack request verification is enabled before accepting production traffic.

## Project Layout

```text
.
├── main.py
├── lib/
│   ├── command_handlers.py
│   ├── models.py
│   ├── utils.py
│   └── services/
├── tests/
├── manifest.json
├── pyproject.toml
├── uv.lock
├── Makefile
├── Dockerfile.test
└── docker-compose-test.yaml
```

## Suggested Improvements

- Enable Slack signature verification and add tests for rejected requests.
- Replace `print` diagnostics with structured logging.
- Add CI that runs `make lint` and `make test`.
- Add unit tests for slash-command routing, interactive payload handling, and Slack Block Kit output.
- Add a `.env.example` with safe placeholder values.
- Consider indexes for active AFK lookup fields in MongoDB if the workspace grows.
