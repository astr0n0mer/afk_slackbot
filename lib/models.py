from datetime import UTC, datetime

from pydantic import BaseModel, Field


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


class AFKRecord(BaseModel):
    created: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    team_id: str = Field(description="")
    team_domain: str = Field(description="")
    channel_id: str = Field(description="")
    channel_name: str = Field(description="")
    user_id: str = Field(description="")
    user_name: str = Field(description="")
    command: str = Field(description="Slack's slash command used to create this record")
    text: str = Field(description="Argument of the triggerer slash command")
    trigger_id: str = Field(description="")
    start_datetime: datetime = Field(description="This timestamp should not be timezone aware (atleast for now)")
    end_datetime: datetime = Field(description="This timestamp should not be timezone aware (atleast for now)")
