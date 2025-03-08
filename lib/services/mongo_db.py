import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from lib.models import AFKRecord

_ = load_dotenv()
if os.path.exists(path="/etc/secrets/.env"):
    _ = load_dotenv("/etc/secrets/.env")

client = AsyncIOMotorClient(os.environ["MONGODB_URI"])
db = client.afk_slackbot

afk_records_collection: AsyncIOMotorCollection[AFKRecord] = db.afk_records
