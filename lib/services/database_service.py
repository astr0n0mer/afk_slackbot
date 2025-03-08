from collections.abc import Sequence
from enum import Enum
from typing import Any, final

from motor.motor_asyncio import AsyncIOMotorCollection

from lib.models import AFKRecord, AFKRecordFilter, AFKStatus
from lib.utils import typed_dict_to_mongodb_query


class WriteMode(Enum):
    OVERWRITE = "w"
    APPEND = "a"


@final
class DatabaseService:
    def __init__(self, collection: AsyncIOMotorCollection[AFKRecord]):
        self.collection = collection

    async def read(self, filter: AFKRecordFilter) -> list[AFKRecord]:
        query = typed_dict_to_mongodb_query(filter)
        cursor = self.collection.find(filter=query)
        objects: list[dict] = await cursor.to_list(length=None)
        records = [AFKRecord.model_validate(o) for o in objects]
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

    async def update(self, records: Sequence[AFKRecord], upsert: bool = False) -> int:
        filter = {"id": {"$in": [record.id for record in records]}}
        update_result = await self.collection.update_many(
            filter=filter,
            update={"$set": [record.model_dump() for record in records]},
            upsert=upsert,
        )
        return update_result.modified_count

    async def clear_afk_status(self, filter: AFKRecordFilter) -> int:
        filter["status"] = [AFKStatus.ACTIVE]
        update_result = await self.collection.update_many(
            filter=typed_dict_to_mongodb_query(filter),
            update={"$set": {"status": AFKStatus.CANCELLED.value}},
        )
        return update_result.modified_count
