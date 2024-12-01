import asyncio
import os
from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import uvicorn
from afk_parser.afk_parser import AFKParser
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, responses
from starlette import exceptions, status

from lib.models import (
    AFKRecord,
    AFKRecordToPrint,
    SlackPostRequestBody,
    SlashSubcommand,
)
from lib.services.database_service import DatabaseService
from lib.services.mongo_db import afk_records_collection
from lib.services.slack_service import SlackService
from lib.utils import format_afk_record_to_print, format_afk_records_to_print

load_dotenv()
#! Reading .env file when app is hosted on render.com
if os.path.exists(path="/etc/secrets/.env"):
    load_dotenv("/etc/secrets/.env")

# storage_service: JSONLService = JSONLService(filepath=Path("./storage/afk_log.jsonl"))
storage_service = DatabaseService(collection=afk_records_collection)
parser: AFKParser = AFKParser()
server_started_at = datetime.now()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     #! code to run before startup
#     # TODO: setup DB connection here
#     # globals()["store_service"] = JSONLService(filepath=Path("./storage/afk_log.jsonl"))
#     # globals()["parser"] = AFKParser()
#     yield
#     #! code to run after shutdown


# app = FastAPI(lifespan=lifespan)
app = FastAPI()


@app.get("/health-check")
def read_health():
    return {
        "server_started_at": server_started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "ok",
    }


# @app.exception_handler(HTTPStatus.NOT_FOUND)
# async def not_found_handler(request: Request, exc: Exception):
#     return responses.RedirectResponse(url="/health-check")


@app.exception_handler(exceptions.HTTPException)
def not_found_handler(_: Request, exc: exceptions.HTTPException):
    if exc.status_code == HTTPStatus.NOT_FOUND:
        return responses.RedirectResponse(url="/health-check")
    return responses.JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.post("/v1/slack_bot")
async def handle_slack_bot_input(request: Request):
    raw_body = await request.body()
    # TODO: validate the request token here

    form_data = await request.form()
    try:
        slack_post_request_body = SlackPostRequestBody.model_validate(
            {k: v for k, v in form_data.items()}
        )
    except:
        # TODO: send a slack message saying the request is malformed
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    slack_service = SlackService(token=os.environ["SLACK_BOT_TOKEN"])
    user_info = await slack_service.get_user_info(
        user_id=slack_post_request_body.user_id
    )
    if user_info is None:
        # TODO: handle if user does not exist
        return "UserInfo is None"

    if slack_post_request_body.text.strip().lower() == SlashSubcommand.LIST.value:
        afk_records = await storage_service.read(
            team_ids=[slack_post_request_body.team_id]
        )
        return (
            SlackService.get_list_response(
                records=format_afk_records_to_print(
                    afk_records=sorted(afk_records, key=lambda r: r.end_datetime),
                    user_info=user_info,
                ),
            )
            if len(afk_records) > 0
            else "No AFK records"
        )
    if slack_post_request_body.text.strip().lower() == SlashSubcommand.TABLE.value:
        afk_records = await storage_service.read(
            team_ids=[slack_post_request_body.team_id]
        )
        return (
            SlackService.get_table_response(
                records=format_afk_records_to_print(
                    afk_records=sorted(afk_records, key=lambda r: r.end_datetime),
                    user_info=user_info,
                ),
            )
            if len(afk_records) > 0
            else "No AFK records"
        )
    if slack_post_request_body.text.strip().lower() == SlashSubcommand.CLEAR.value:
        records_updated = await storage_service.clear_afk_status(
            team_id=slack_post_request_body.team_id,
            user_id=slack_post_request_body.user_id,
        )
        return (
            f"{records_updated} AFK record{'s' if records_updated > 1 else ''} cleared"
            if records_updated
            else "No AFK records"
        )

    parse_result = parser.parse_dates(
        phrase=slack_post_request_body.text,
        tz_offset=user_info.tz_offset,
    )
    if not parse_result:
        # TODO: trigger error handling mechanism
        return {"foo": "bar"}

    afk_record = AFKRecord(
        **slack_post_request_body.model_dump(),
        start_datetime=(parse_result[0]).timestamp(),
        end_datetime=(parse_result[1]).timestamp(),
    )

    if (
        not slack_post_request_body.text.strip()
        .lower()
        .startswith(SlashSubcommand.ADD.value)
    ):
        await storage_service.clear_afk_status(
            team_id=afk_record.team_id, user_id=afk_record.user_id
        )

    await storage_service.write(records=[afk_record])
    response = SlackService.get_list_response(
        records=[format_afk_record_to_print(afk_record=afk_record, user_info=user_info)]
    )
    return response


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    config = uvicorn.Config(
        app=app,
        loop=event_loop,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
        server_header=False,
    )
    server = uvicorn.Server(config=config)
    event_loop.run_until_complete(server.serve())
