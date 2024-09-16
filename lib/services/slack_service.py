import requests

from lib.models import UserInfo, AFKRecordToPrint



class SlackService:
    def __init__(self, token: str):
        self.token = token

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        api_url = "https://slack.com/api/users.info"
        query_params = {"user": user_id, "include_locale": True}
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        try:
            # async with httpx.AsyncClient() as client:
            response = requests.post(url=api_url, headers=headers, params=query_params)
            response_json = response.json()
            user = response_json.get("user", None)
            return UserInfo.model_validate(user)
        except Exception:
            print("could not parse")
            return None

    @staticmethod
    def get_list_response(records: list[AFKRecordToPrint]) -> dict:
        return {
            "blocks": [
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "\n".join(
                                (
                                    f"*{record.real_name}* (afk {record.text})",
                                    f"From: {record.start_datetime}",
                                    f"To: {record.end_datetime}",
                                ),
                            ),
                        }
                        for record in records
                    ],
                },
            ],
        }

    @staticmethod
    def get_table_response(records: list[AFKRecordToPrint]) -> dict:
        max_len_real_name = 0
        max_len_start_datetime = 0
        max_len_end_datetime = 0
        for record in records:
            max_len_real_name = max(max_len_real_name, len(record.real_name))
            max_len_start_datetime = max(max_len_start_datetime, len(record.start_datetime))
            max_len_end_datetime = max(max_len_end_datetime, len(record.end_datetime))
        header_block = " | ".join(
            (
                "User".center(max_len_real_name, " "),
                "AFK Start".center(max_len_start_datetime, " "),
                "AFK End".center(max_len_end_datetime, " "),
            ),
        )
        divider_block = " | ".join(("-" * max_len_real_name, "-" * max_len_start_datetime, "-" * max_len_end_datetime))
        table_block = [
            " | ".join(
                (
                    record.real_name.ljust(max_len_real_name, " "),
                    record.start_datetime.ljust(max_len_start_datetime, " "),
                    record.end_datetime.ljust(max_len_end_datetime, " "),
                ),
            )
            for record in records
        ]

        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "```" + "\n".join((header_block, divider_block, *table_block)) + "```",
                    },
                },
            ],
        }
