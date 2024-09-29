from datetime import datetime, timedelta
from typing import Sequence

from babel import dates

from lib.models import AFKRecord, AFKRecordToPrint, UserInfo


def format_afk_record_to_print(
    afk_record: AFKRecord, user_info: UserInfo
) -> AFKRecordToPrint:
    delta = timedelta(seconds=user_info.tz_offset)
    locale = user_info.locale.replace("-", "_")
    return AFKRecordToPrint(
        text=afk_record.text,
        real_name=user_info.real_name,
        start_datetime=dates.format_datetime(
            datetime.fromtimestamp(afk_record.start_datetime) + delta,
            locale=locale,
            format="short",
        ),
        end_datetime=dates.format_datetime(
            datetime.fromtimestamp(afk_record.end_datetime) + delta,
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
