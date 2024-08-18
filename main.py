import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from http import HTTPStatus

import uvicorn
from afk_parser.afk_parser import AFKParser
from fastapi import FastAPI, HTTPException, Request, responses
from starlette import exceptions, status

from lib.models import AFKRecord, SlackPostRequestBody, SlashSubcommand
from lib.services.database_service import DatabaseService
from lib.services.mongo_db import afk_records_collection
from lib.utils import format_datetime

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


def get_response(records: list[AFKRecord]) -> dict:
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        (
                            f"*{record.user_name}* (afk {record.text})",
                            f"From: {format_datetime(datetime.fromtimestamp(record.start_datetime))}\tTo: {format_datetime(datetime.fromtimestamp(record.end_datetime))}",
                        ),
                    ),
                },
            }
            for record in records
        ],
    }


@app.get("/health-check")
def read_health():
    return {"server_started_at": server_started_at.strftime("%Y-%m-%d %H:%M:%S"), "status": "ok"}


# @app.exception_handler(HTTPStatus.NOT_FOUND)
# async def not_found_handler(request: Request, exc: Exception):
#     return responses.RedirectResponse(url="/health-check")


@app.exception_handler(exceptions.HTTPException)
def not_found_handler(request: Request, exc: exceptions.HTTPException):
    if exc.status_code == HTTPStatus.NOT_FOUND:
        return responses.RedirectResponse(url="/health-check")
    return responses.JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.post("/v1/slack_bot")
async def handle_slack_bot_input(request: Request):
    raw_body = await request.body()
    # TODO: validate the request token here

    form_data = await request.form()
    try:
        slack_post_request_body = SlackPostRequestBody.parse_obj({k: v for k, v in form_data.items()})
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if slack_post_request_body.text.strip().lower() == SlashSubcommand.LIST:
        afk_records = await storage_service.read(team_ids=[slack_post_request_body.team_id])
        return get_response(records=afk_records) if len(afk_records) > 0 else "No AFK records"
    elif slack_post_request_body.text.strip().lower() == SlashSubcommand.CLEAR:
        records_updated = await storage_service.clear_afk_status(
            team_id=slack_post_request_body.team_id,
            user_id=slack_post_request_body.user_id,
        )
        return (
            f"{records_updated} AFK record{'s' if records_updated > 1 else ''} cleared"
            if records_updated
            else "No AFK records"
        )

    parse_result = parser.parse_dates(phrase=slack_post_request_body.text)
    if not parse_result:
        # TODO: trigger error handling mechanism
        return {"foo": "bar"}

    afk_record = AFKRecord(
        **slack_post_request_body.model_dump(),
        start_datetime=parse_result[0].timestamp(),
        end_datetime=parse_result[1].timestamp(),
    )
    # TODO: uncomment before running in production
    # await storage_service.clear_afk_status(team_id=afk_record.team_id, user_id=afk_record.user_id)
    await storage_service.write(records=[afk_record])
    response = get_response(records=[afk_record])
    return response


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    config = uvicorn.Config(app=app, loop=event_loop, reload=True, server_header=False)
    server = uvicorn.Server(config=config)
    event_loop.run_until_complete(server.serve())
