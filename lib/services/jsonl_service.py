import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Sequence

from lib.models import AFKRecord, AFKStatus


class WriteMode(Enum):
    OVERWRITE = "w"
    APPEND = "a"


class JSONLService:
    def __init__(self, filepath: Path):
        if filepath.suffix.lower() != ".jsonl":
            raise ValueError(f"Invalid filepath: {filepath}. Only .jsonl files supported")
        self.filepath = filepath

    async def read(
        self,
        ids: Sequence[str] = (),
        team_ids: Sequence[str] = (),
        user_ids: Sequence[str] = (),
        user_names: Sequence[str] = (),
        status: Sequence[AFKStatus] | None = None,
        read_from: datetime | None = None,
    ) -> list[AFKRecord]:
        status_strings = [s.value for s in (status or [AFKStatus.ACTIVE])]
        read_from_timestamp = (read_from or datetime.now()).timestamp()
        read_records: list[AFKRecord] = []
        with open(self.filepath) as file:
            for line in file:
                record = AFKRecord.parse_obj(json.loads(line))
                if (
                    (record.id in ids if ids else True)
                    and (record.team_id in team_ids if team_ids else True)
                    and (record.user_id in user_ids if user_ids else True)
                    and (record.user_name in user_names if user_names else True)
                    and record.status in status_strings
                    and (record.end_datetime >= read_from_timestamp)
                ):
                    read_records.append(record)
        return read_records

    async def write(self, records: Sequence[AFKRecord], mode: WriteMode = WriteMode.APPEND) -> Sequence[AFKRecord]:
        json_string = "\n".join(json.dumps(record.model_dump()) for record in records)
        with open(self.filepath, mode.value) as file:
            file.write(json_string + "\n")
        return records

    async def update(self, records: Sequence[AFKRecord], upsert=False) -> Sequence[AFKRecord]:
        records_from_store = await self.read(
            status=[AFKStatus.ACTIVE, AFKStatus.CANCELLED],
            read_from=datetime.min.replace(year=1970),
        )
        records_to_update_map = {record.id: record for record in records}
        updated_records = [
            records_to_update_map.pop(record.id) if record.id in records_to_update_map else record
            # records_to_update_map.get(record.id, record)
            for record in records_from_store
        ] + (list(records_to_update_map.values()) if upsert else [])
        await self.write(records=updated_records, mode=WriteMode.OVERWRITE)
        return records
