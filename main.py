from datetime import UTC, datetime
from http import HTTPStatus
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, responses
from starlette import exceptions, status
import uvicorn

from lib.command_handlers import (
    handle_clear_subcommand,
    handle_create_subcommand,
    handle_list_subcommand,
    handle_table_subcommand,
)
from lib.models import SlackPostRequestBody, SlashSubcommand
from lib.services import DatabaseService, SlackService, afk_records_collection

_ = load_dotenv()
#! Reading .env file when app is hosted on render.com
if os.path.exists(path="/etc/secrets/.env"):
    _ = load_dotenv("/etc/secrets/.env")

storage_service = DatabaseService(collection=afk_records_collection)
server_started_at = datetime.now(tz=UTC)


app = FastAPI()


@app.get("/health-check")
def read_health():
    return {
        "server_started_at": server_started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "ok",
    }


@app.exception_handler(exceptions.HTTPException)
def not_found_handler(_: Request, exc: exceptions.HTTPException):
    if exc.status_code == HTTPStatus.NOT_FOUND:
        return responses.RedirectResponse(url="/health-check")
    return responses.JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.post("/v1/slack_bot")
async def handle_slack_bot_input(request: Request):
    raw_body = await request.body()
    slack_service = SlackService(token=os.environ["SLACK_BOT_TOKEN"])
    is_valid_request = await slack_service.validate_request(
        body=raw_body,
        headers=dict(request.headers),
    )
    if not is_valid_request:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    form_data = await request.form()
    try:
        slack_post_request_body = SlackPostRequestBody.model_validate(
            {k: v for k, v in form_data.items()}
        )
    except Exception as e:
        # TODO: send a slack message saying the request is malformed
        print(f"Error: {e}")  # TODO: replace with logger
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    user_info = await slack_service.get_user_info(
        user_id=slack_post_request_body.user_id
    )
    if user_info is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if slack_post_request_body.text.strip().lower() == SlashSubcommand.LIST.value:
        return await handle_list_subcommand(
            service=storage_service, user_info=user_info
        )
    if slack_post_request_body.text.strip().lower() == SlashSubcommand.TABLE.value:
        return await handle_table_subcommand(
            service=storage_service, user_info=user_info
        )
    if slack_post_request_body.text.strip().lower() == SlashSubcommand.CLEAR.value:
        return await handle_clear_subcommand(
            service=storage_service, user_info=user_info
        )
    return await handle_create_subcommand(
        slack_post_request_body=slack_post_request_body,
        service=storage_service,
        user_info=user_info,
    )


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=os.environ.get("ENABLE_HOT_RELOAD", "false").lower() == "true",
        reload_dirs=["."],
        server_header=False,
    )
