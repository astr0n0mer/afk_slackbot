import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

if not load_dotenv():
    raise OSError("No environment variables found")

client = AsyncIOMotorClient(os.getenv("MONGODB_URI", None))
db = client.afk_slackbot

afk_records = db.afk_records
