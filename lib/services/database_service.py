from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from lib.models import AFKRecord, AFKStatus
from lib.services.jsonl_service import WriteMode


class DatabaseService:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def read(
        self,
        # TODO: replace the following with a filter DTO
        ids: Sequence[str] = (),
        team_ids: Sequence[str] = (),
        user_ids: Sequence[str] = (),
        status: Sequence[AFKStatus] | None = None,
        read_from: datetime | None = None,
    ) -> list[AFKRecord]:
        status_strings = [s.value for s in (status or [AFKStatus.ACTIVE])]
        read_from_timestamp = (
            read_from or datetime.now(tz=UTC).replace(tzinfo=None)
        ).timestamp()

        filter = (
            ({"id": {"$in": ids}} if ids else {})
            | ({"team_id": {"$in": team_ids}} if team_ids else {})
            | ({"user_id": {"$in": user_ids}} if user_ids else {})
            | ({"status": {"$in": status_strings}} if status_strings else {})
            | ({"end_datetime": {"$gte": read_from_timestamp}})
        )
        cursor = self.collection.find(filter=filter)
        objects = await cursor.to_list(length=None)
        records = [AFKRecord.model_validate(object) for object in objects]
        return records

    async def write(
        self, records: Sequence[AFKRecord], mode: WriteMode = WriteMode.APPEND
    ) -> list[Any]:
        if mode == WriteMode.OVERWRITE:
            _ = await self.collection.delete_many(filter={})
        insert_result = await self.collection.insert_many(
            documents=(record.model_dump() for record in records)
        )
        return insert_result.inserted_ids

    async def update(self, records: Sequence[AFKRecord], upsert=False) -> int:
        filter = {"id": {"$in": [record.id for record in records]}}
        update_result = await self.collection.update_many(
            filter=filter,
            update={"$set": [record.model_dump() for record in records]},
            upsert=upsert,
        )
        return update_result.modified_count

    async def clear_afk_status(self, team_id: str, user_id: str) -> int:
        filter = {
            "team_id": team_id,
            "user_id": user_id,
            "status": AFKStatus.ACTIVE.value,
        }
        update_result = await self.collection.update_many(
            filter=filter,
            update={"$set": {"status": AFKStatus.CANCELLED.value}},
        )
        return update_result.modified_count
