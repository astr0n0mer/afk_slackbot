from datetime import datetime, timedelta
from typing import Sequence

from babel import dates

from lib.models import AFKRecord, AFKRecordToPrint, UserInfo


# TODO: this is unused, can probably remove
def format_datetime(d: datetime) -> str:
    is_today = d.date().__eq__(datetime.today())
    is_tomorrow = d.date().__eq__(datetime.today() + timedelta(days=1))
    string = (
        d.strftime("Today %I:%M%p")
        if is_today
        else d.strftime("Tomorrow %I:%M%p")
        if is_tomorrow
        else d.strftime("%Y-%m-%d %I:%M%p")
    )
    return string


def format_afk_record_to_print(afk_record: AFKRecord, user_info: UserInfo) -> AFKRecordToPrint:
    delta = timedelta(seconds=user_info.tz_offset)
    locale = user_info.locale.replace("-", "_")
    return AFKRecordToPrint(
        text=afk_record.text,
        real_name=user_info.real_name,
        start_datetime=dates.format_datetime(datetime.fromtimestamp(afk_record.start_datetime) + delta, locale=locale),
        end_datetime=dates.format_datetime(datetime.fromtimestamp(afk_record.end_datetime) + delta, locale=locale),
    )


def format_afk_records_to_print(afk_records: Sequence[AFKRecord], user_info: UserInfo) -> list[AFKRecordToPrint]:
    return list(map(lambda record: format_afk_record_to_print(afk_record=record, user_info=user_info), afk_records))
