from datetime import datetime, timedelta


def format_datetime(d: datetime) -> str:
    is_today = d.date().__eq__(datetime.today())
    is_tomorrow = d.date().__eq__(datetime.today() + timedelta(days=1))
    print(f"{d.date()=} {datetime.today()=} {is_today=} {is_tomorrow=}")
    string = (
        d.strftime("Today %I:%M%p")
        if is_today
        else d.strftime("Tomorrow %I:%M%p")
        if is_tomorrow
        else d.strftime("%Y-%m-%d %I:%M%p")
    )
    return string
