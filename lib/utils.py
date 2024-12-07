from collections.abc import Sequence
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from typing import Any

from babel import dates

from lib.models import AFKRecord, AFKRecordToPrint, UserInfo


def typed_dict_to_mongodb_query(typed_dict: Mapping[str, Any]):
    filters = [{k: {"$in": v} for k, v in typed_dict.items() if v}]
    query = {"$or": filters} if filters else {}
    return query


def format_afk_record_to_print(
    afk_record: AFKRecord, user_info: UserInfo
) -> AFKRecordToPrint:
    locale = user_info.locale.replace("-", "_")
    custom_timezone = timezone(timedelta(seconds=user_info.tz_offset))
    users_local_now = datetime.now(tz=custom_timezone)
    users_local_time_zone = users_local_now.tzinfo

    return AFKRecordToPrint(
        text=afk_record.text,
        real_name=user_info.real_name,
        start_datetime=dates.format_datetime(
            datetime.fromtimestamp(afk_record.start_datetime, tz=users_local_time_zone),
            locale=locale,
            format="short",
        ),
        end_datetime=dates.format_datetime(
            datetime.fromtimestamp(afk_record.end_datetime, tz=users_local_time_zone),
            locale=locale,
            format="short",
        ),
    )


def format_afk_records_to_print(
    afk_records: Sequence[AFKRecord], user_info: UserInfo
) -> list[AFKRecordToPrint]:
    return list(
        map(
            lambda record: format_afk_record_to_print(
                afk_record=record, user_info=user_info
            ),
            afk_records,
        )
    )
