import os
from typing import Any

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

_ = load_dotenv()
if os.path.exists(path="/etc/secrets/.env"):
    _ = load_dotenv("/etc/secrets/.env")

client = AsyncIOMotorClient(os.environ["MONGODB_URI"])
db = client.afk_slackbot

afk_records_collection: AsyncIOMotorCollection[dict[str, Any]] = db.afk_records
