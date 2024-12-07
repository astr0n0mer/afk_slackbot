from datetime import UTC, datetime

from afk_parser.afk_parser import AFKParser

from lib.models import AFKRecord, AFKStatus, SlackPostRequestBody, UserInfo
from lib.services import DatabaseService, SlackService
from lib.utils import format_afk_record_to_print, format_afk_records_to_print


async def handle_list_subcommand(service: DatabaseService, user_info: UserInfo):
    afk_records = await service.read(
        {
            "end_datetime": datetime.now(tz=UTC),
            "status": [AFKStatus.ACTIVE],
            "team_id": [user_info.team_id],
        }
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


async def handle_table_subcommand(service: DatabaseService, user_info: UserInfo):
    afk_records = await service.read(
        {
            "end_datetime": datetime.now(tz=UTC),
            "status": [AFKStatus.ACTIVE],
            "team_id": [user_info.team_id],
        }
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


async def handle_clear_subcommand(service: DatabaseService, user_info: UserInfo):
    records_updated = await service.clear_afk_status(
        {"team_id": [user_info.team_id], "user_id": [user_info.id]}
    )
    return (
        f"{records_updated} AFK record{'s' if records_updated > 1 else ''} cleared"
        if records_updated
        else "No AFK records"
    )


async def handle_create_subcommand(
    slack_post_request_body: SlackPostRequestBody,
    service: DatabaseService,
    user_info: UserInfo,
):
    parse_result = AFKParser().parse_dates(
        phrase=slack_post_request_body.text, tz_offset=user_info.tz_offset
    )
    if not parse_result:
        # TODO: trigger error handling mechanism
        return {"foo": "bar"}

    afk_record = AFKRecord(
        **slack_post_request_body.model_dump(),
        start_datetime=(parse_result[0]).timestamp(),
        end_datetime=(parse_result[1]).timestamp(),
    )
    _ = await service.write(records=[afk_record])
    return SlackService.get_list_response(
        records=[format_afk_record_to_print(afk_record=afk_record, user_info=user_info)]
    )
