from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

AFKRecord_VERSION = 1


class AFKStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class SlashSubcommand(Enum):
    ADD = "add"
    CLEAR = "clear"
    LIST = "list"
    TABLE = "table"


class AFKRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="")
    created: float = Field(default_factory=lambda: datetime.now(tz=UTC).timestamp())
    version: int = Field(default=AFKRecord_VERSION, description="")
    team_id: str = Field(description="")
    team_domain: str = Field(description="")
    channel_id: str = Field(description="")
    channel_name: str = Field(description="")
    user_id: str = Field(description="")
    user_name: str = Field(description="")
    command: str = Field(description="Slack's slash command used to create this record")
    text: str = Field(description="Argument of the triggerer slash command")
    trigger_id: str = Field(description="")
    start_datetime: float = Field(description="This timestamp should not be timezone aware (atleast for now)")
    end_datetime: float = Field(description="This timestamp should not be timezone aware (atleast for now)")
    status: str = Field(default=AFKStatus.ACTIVE.value, description="")


class AFKRecordToPrint(BaseModel):
    text: str = Field(description="Text used to trigger AFK Slackbot")
    real_name: str = Field(description="User's display name on Slack")
    start_datetime: str = Field(description="AFK start datetime as str")
    end_datetime: str = Field(description="AFK end datetime as str")


class SlackPostRequestBody(BaseModel):
    token: str = Field(description="")  # TODO: should not be using this
    team_id: str = Field(description="")
    team_domain: str = Field(description="")
    channel_id: str = Field(description="")
    channel_name: str = Field(description="")
    user_id: str = Field(description="")
    user_name: str = Field(description="")
    command: str = Field(description="")
    text: str = Field(description="")
    api_app_id: str = Field(description="")
    is_enterprise_install: bool = Field(description="")
    response_url: str = Field(description="")
    trigger_id: str = Field(description="")


class UserInfo(BaseModel):
    locale: str = Field(description="User locale")
    real_name: str = Field(description="User's display name on Slack")
    tz: str = Field(description="Timezone info as A/B")  # TODO: unused
    tz_offset: int = Field(description="Number of seconds offset from UTC")
