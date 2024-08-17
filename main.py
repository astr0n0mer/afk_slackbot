from fastapi import FastAPI, Request

from afk_parser.lib.afk_parser import AFKParser
from lib.models import AFKRecord, SlackPostRequestBody
from lib.utils import format_datetime

app = FastAPI()
parser = AFKParser()
afk_records: list[AFKRecord] = []


# TODO: this endpoint can be removed
@app.get("/")
def read_root():
    return {"foo": "bar"}


@app.post("/v1/slack_bot")
async def handle_slack_bot_input(request: Request):
    raw_body = await request.body()
    form_data = await request.form()
    slack_post_request_body = SlackPostRequestBody.parse_obj({k: v for k, v in form_data.items()})

    parse_result = parser.parse_dates(phrase=slack_post_request_body.text)
    if not parse_result:
        # TODO: trigger error handling mechanism
        return {"foo": "bar"}

    afk_record = AFKRecord(
        **slack_post_request_body.dict(),
        start_datetime=parse_result[0],
        end_datetime=parse_result[1],
    )
    afk_records.append(afk_record)

    response = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        (
                            f"*{afk_record.user_name}* (afk {afk_record.text})",
                            f"From: {format_datetime(afk_record.start_datetime)}\tTo: {format_datetime(afk_record.end_datetime)}",
                        ),
                    ),
                },
            }
            for afk_record in afk_records
        ],
    }

    if slack_post_request_body.text == "list":
        raise NotImplementedError("will implement this later")
    else:
        for key, value in form_data.items():
            print(key, "\t", value)
    return response
