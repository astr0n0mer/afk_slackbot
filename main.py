from datetime import UTC, datetime
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, responses
from pydantic import ValidationError
from slack_sdk.signature import SignatureVerifier
from starlette import status
import uvicorn

from lib.command_handlers import (
    handle_clear_subcommand,
    handle_create_subcommand,
    handle_list_subcommand,
    handle_table_subcommand,
    send_slack_message,
)
from lib.models import (
    AFKRecord,
    SlackPayloadType,
    SlackPostRequestBody,
    SlashSubcommand,
)
from lib.services import DatabaseService, SlackService, afk_records_collection

_ = load_dotenv()
#! Reading .env file when app is hosted on render.com
if os.path.exists(path="/etc/secrets/.env"):
    _ = load_dotenv("/etc/secrets/.env")

server_started_at = datetime.now(tz=UTC)
storage_service = DatabaseService(collection=afk_records_collection)
slack_service = SlackService(token=os.environ["SLACK_BOT_TOKEN"])


app = FastAPI()


@app.get("/")
def read_root():
    return responses.RedirectResponse(url="/health-check")


@app.get("/health-check")
def read_health():
    return {
        "server_started_at": server_started_at,
        "status": "ok",
    }


@app.post("/v1/slack_bot")
async def handle_slack_bot_input(request: Request):
    raw_body = await request.body()

    # TODO: enable this before commit
    # is_valid_request = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"]).is_valid_request(
    #     body=raw_body, headers=dict(request.headers)
    # )
    # if not is_valid_request:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    form_data = await request.form()
    try:
        slack_post_request_body = SlackPostRequestBody.model_validate(
            {k: v for k, v in form_data.items()}
        )
    except ValidationError as e:
        # TODO: send a slack message saying the request is malformed
        print(f"Error: {e}")  # TODO: replace with logger
        print(f"Form data: {form_data}")  # TODO: replace with logger
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
        database_service=storage_service,
        slack_service=slack_service,
        user_info=user_info,
    )


@app.post("/v1/interactive_message")
async def handle_interactive_message(request: Request):
    form_data = await request.form()
    payload = json.loads(form_data.get("payload", "{}"))
    print(f"Payload: {json.dumps(payload, indent=2)}")  # TODO: replace with logger
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if next(
        (
            action.get("action_id", "") == "submit_button"
            for action in payload.get("actions", [])
        ),
        "",
    ):
        payload_type: str = payload.get("type", "")
        if payload_type == SlackPayloadType.BLOCK_ACTIONS.value:
            afk_record = AFKRecord.from_interactive_request_body(payload=payload)
            user_info = await slack_service.get_user_info(user_id=afk_record.user_id)
            if user_info is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return await send_slack_message(
                afk_record=afk_record,
                database_service=storage_service,
                slack_service=slack_service,
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
