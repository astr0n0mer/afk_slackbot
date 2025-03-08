from collections.abc import Sequence
from datetime import UTC, datetime
from enum import Enum
from typing import Any, TypedDict
from uuid import uuid4

from fastapi.datastructures import FormData
from pydantic import BaseModel, Field

AFKRecord_VERSION = 1


class AFKStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class SlackPayloadType(Enum):
    BLOCK_ACTIONS = "block_actions"
    VIEW_SUBMISSION = "view_submission"


class SlashSubcommand(Enum):
    CLEAR = "clear"
    LIST = "list"
    TABLE = "table"


class AFKRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="")
    channel_id: str = Field(description="")
    command: str = Field(description="Slack's slash command used to create this record")
    created: float = Field(default_factory=lambda: datetime.now(tz=UTC).timestamp())
    end_datetime: float = Field(
        description="This timestamp should not be timezone aware (atleast for now)"
    )
    start_datetime: float = Field(
        description="This timestamp should not be timezone aware (atleast for now)"
    )
    status: str = Field(default=AFKStatus.ACTIVE.value, description="")
    team_id: str = Field(description="")
    text: str = Field(description="Argument of the triggerer slash command")
    trigger_id: str = Field(description="")
    user_id: str = Field(description="")
    version: int = Field(
        default=AFKRecord_VERSION,
        description="Model version for backward compatibility",
    )

    @staticmethod
    def from_interactive_request_body(payload: dict[str, Any]) -> "AFKRecord":
        return AFKRecord(
            channel_id=payload["channel"]["id"],
            command="/afk",
            end_datetime=float(
                payload["state"]["values"]["afk_end_input"]["end_time_picker"][
                    "selected_date_time"
                ]
            ),
            start_datetime=float(
                payload["state"]["values"]["afk_start_input"]["start_time_picker"][
                    "selected_date_time"
                ]
            ),
            team_id=payload["team"]["id"],
            text="interactive_message",
            trigger_id=str(payload["trigger_id"]),
            user_id=payload["user"]["id"],
        )


class AFKRecordFilter(TypedDict, total=False):
    id: Sequence[str]
    end_datetime: datetime
    status: Sequence[AFKStatus]
    team_id: Sequence[str]
    user_id: Sequence[str]


class AFKRecordToPrint(BaseModel):
    end_datetime: str = Field(description="AFK end datetime as str")
    real_name: str = Field(description="User's display name on Slack")
    start_datetime: str = Field(description="AFK start datetime as str")
    text: str = Field(description="Text used to trigger AFK Slackbot")


class SlackPostRequestBody(BaseModel):
    api_app_id: str = Field(description="")
    channel_id: str = Field(description="")
    command: str = Field(description="")
    is_enterprise_install: bool = Field(description="")
    response_url: str = Field(description="")
    team_id: str = Field(description="")
    text: str = Field(description="")
    token: str = Field(description="")  # TODO: should not be using this
    trigger_id: str = Field(description="")
    user_id: str = Field(description="")


class UserInfo(BaseModel):
    id: str = Field(description="User ID")
    locale: str = Field(description="User locale")
    real_name: str = Field(description="User's display name on Slack")
    team_id: str = Field(description="Slack team id")
    tz_offset: int = Field(description="Number of seconds offset from UTC")
