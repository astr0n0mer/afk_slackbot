import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

client = AsyncIOMotorClient(os.environ["MONGODB_URI"])
db = client.afk_slackbot

afk_records_collection = db.afk_records
