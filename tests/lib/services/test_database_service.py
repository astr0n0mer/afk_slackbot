from datetime import UTC, datetime, timedelta
import os
import sys
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from lib.models import AFKRecord, AFKRecord_VERSION, AFKStatus
from lib.services.database_service import DatabaseService
from lib.services.jsonl_service import WriteMode


@pytest.fixture(scope="function", autouse=True)
async def db_service():
    client = AsyncIOMotorClient(os.environ["MONGODB_URI"])
    db = client.afk_slackbot
    collection = db.afk_records

    service = DatabaseService(collection=collection)
    yield service
    _ = await collection.delete_many({})
    client.close()


@pytest.fixture(scope="function")
def placeholder_afk_record():
    return AFKRecord(
        id=str(uuid4()),
        created=datetime.now(tz=UTC).timestamp(),
        version=AFKRecord_VERSION,
        team_id="team_id_0",
        channel_id="channel_id_0",
        user_id="user_id_0",
        command="command_0",
        text="text_0",
        trigger_id="trigger_id_0",
        start_datetime=datetime.now(tz=UTC).timestamp(),
        end_datetime=datetime.now(tz=UTC).timestamp(),
        status=AFKStatus.ACTIVE.value,
    )


@pytest.mark.asyncio
async def test_read__with_no_filters(db_service: DatabaseService):
    result = await db_service.read()
    assert result == []


@pytest.mark.asyncio
async def test_read__with_read_from_timestamp_filter(
    db_service: DatabaseService, placeholder_afk_record: AFKRecord
):
    # Arrange
    now = datetime.now(tz=UTC)
    afk_records = [
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now - timedelta(hours=1)).timestamp(),
        ),
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now + timedelta(hours=1)).timestamp(),
        ),
    ]
    _ = await db_service.write(afk_records)
    expected_result = [afk_records[1]]

    # Act
    result = await db_service.read(read_from=now)

    # Assert
    assert result == expected_result


@pytest.mark.asyncio
async def test_read__with_default_read_from_timestamp_filter(
    db_service: DatabaseService, placeholder_afk_record: AFKRecord
):
    # Arrange
    now = datetime.now(tz=UTC)
    afk_records = [
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now - timedelta(hours=1)).timestamp(),
        ),
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now + timedelta(hours=1)).timestamp(),
        ),
    ]
    _ = await db_service.write(afk_records)
    expected_result = [afk_records[1]]

    # Act
    result = await db_service.read()

    # Assert
    assert result == expected_result


@pytest.mark.asyncio
async def test_write__with_default_mode(
    db_service: DatabaseService, placeholder_afk_record: AFKRecord
):
    # Arrange
    now = datetime.now(tz=UTC)
    existing_afk_records = [
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now + timedelta(hours=1)).timestamp(),
        ),
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now + timedelta(hours=2)).timestamp(),
        ),
    ]
    await db_service.write(existing_afk_records)
    new_afk_record = AFKRecord(
        **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
        end_datetime=(now + timedelta(hours=3)).timestamp(),
    )
    expected_afk_records = existing_afk_records + [new_afk_record]

    # Act
    _ = await db_service.write([new_afk_record])
    result = await db_service.read()

    # Assert
    assert result == expected_afk_records


@pytest.mark.asyncio
async def test_write__with_overwrite_mode(
    db_service: DatabaseService, placeholder_afk_record: AFKRecord
):
    # Arrange
    now = datetime.now(tz=UTC)
    existing_afk_records = [
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now + timedelta(hours=1)).timestamp(),
        ),
        AFKRecord(
            **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
            end_datetime=(now + timedelta(hours=2)).timestamp(),
        ),
    ]
    await db_service.write(existing_afk_records)
    new_afk_record = AFKRecord(
        **placeholder_afk_record.model_dump(exclude={"end_datetime"}),
        end_datetime=(now + timedelta(hours=3)).timestamp(),
    )
    expected_afk_records = [new_afk_record]

    # Act
    _ = await db_service.write([new_afk_record], mode=WriteMode.OVERWRITE)
    result = await db_service.read()

    # Assert
    assert result == expected_afk_records


@pytest.mark.asyncio
async def test_clear_afk_status(
    db_service: DatabaseService, placeholder_afk_record: AFKRecord
):
    # Arrange
    user_id = "user_id_1"
    existing_afk_records = [
        AFKRecord(
            **placeholder_afk_record.model_dump(
                exclude={"team_id", "user_id", "status"}
            ),
            team_id="team_id_1",
            user_id=user_id,
            status=AFKStatus.ACTIVE.value,
        ),
        AFKRecord(
            **placeholder_afk_record.model_dump(
                exclude={"team_id", "user_id", "status"}
            ),
            team_id="team_id_2",
            user_id=user_id,
            status=AFKStatus.ACTIVE.value,
        ),
    ]
    _ = await db_service.write(existing_afk_records)
    expected_afk_records = existing_afk_records[:-1] + [
        AFKRecord(
            **existing_afk_records[-1].model_dump(exclude={"status"}),
            status=AFKStatus.CANCELLED.value,
        )
    ]

    # Act
    await db_service.clear_afk_status(team_id="team_id_2", user_id=user_id)
    result = await db_service.read(
        status=[AFKStatus.ACTIVE, AFKStatus.CANCELLED],
        read_from=datetime.now(tz=UTC) - timedelta(hours=1),
    )

    # Assert
    assert result == expected_afk_records
