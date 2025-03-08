from collections.abc import Sequence
from typing import final

import requests
from slack_sdk import WebClient
from slack_sdk.models.blocks import (
    ActionsBlock,
    Block,
    ButtonElement,
    DateTimePickerElement,
    InputBlock,
    MarkdownTextObject,
    SectionBlock,
)

from lib.models import AFKRecordToPrint, UserInfo


@final
class SlackService:
    def __init__(self, token: str):
        self.token = token
        self.web_client = WebClient(token=token)

    @staticmethod
    def get_custom_input_block(text: str, initial_date_time: int):
        return {
            "blocks": [
                block.to_dict()
                for block in [
                    SectionBlock(
                        text=f'Could not parse "{text}", please enter AFK details manually'
                    ),
                    InputBlock(
                        block_id="afk_start_input",
                        label="Start Time",
                        element=DateTimePickerElement(
                            action_id="start_time_picker",
                            initial_date_time=initial_date_time,
                        ),
                    ),
                    InputBlock(
                        block_id="afk_end_input",
                        label="End Time",
                        element=DateTimePickerElement(
                            action_id="end_time_picker",
                            initial_date_time=initial_date_time,
                        ),
                    ),
                    ActionsBlock(
                        block_id="submit_block",
                        elements=[
                            ButtonElement(
                                text="Submit",
                                action_id="submit_button",
                                style="primary",
                            )
                        ],
                    ),
                ]
            ]
        }

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        api_url = "https://slack.com/api/users.info"
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        query_params = {"user": user_id, "include_locale": True}
        try:
            response = requests.post(url=api_url, headers=headers, params=query_params)
            response_json = response.json()
            user = response_json.get("user", None)
            return UserInfo.model_validate(user)
        except Exception as e:
            print(f"Error: {e}")  # TODO: replace with logger
            return None

    @staticmethod
    def get_list_response(records: list[AFKRecordToPrint]):
        return [
            SectionBlock(
                fields=[
                    MarkdownTextObject(
                        text="\n".join(
                            [
                                f"*{record.real_name}* (afk {record.text})",
                                f"From: {record.start_datetime}",
                                f"Upto: {record.end_datetime}",
                            ]
                        )
                    )
                    for record in records
                ]
            )
        ]

    @staticmethod
    def get_table_response(records: list[AFKRecordToPrint]):
        max_len_real_name = len(max(records, key=lambda r: len(r.real_name)).real_name)
        max_len_start_datetime = len(
            max(records, key=lambda r: len(r.start_datetime)).start_datetime
        )
        max_len_end_datetime = len(
            max(records, key=lambda r: len(r.end_datetime)).end_datetime
        )
        header_block = " | ".join(
            (
                "User".center(max_len_real_name, " "),
                "AFK Start".center(max_len_start_datetime, " "),
                "AFK End".center(max_len_end_datetime, " "),
            ),
        )
        divider_block = " | ".join(
            (
                "-" * max_len_real_name,
                "-" * max_len_start_datetime,
                "-" * max_len_end_datetime,
            )
        )
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

        return MarkdownTextObject(
            text="```" + "\n".join([header_block, divider_block, *table_block]) + "```"
        )

    def post_message(self, channel_id: str, blocks: Sequence[Block]):
        return self.web_client.chat_postMessage(
            channel=channel_id, blocks=blocks, text="Message from AFK Slackbot"
        )
