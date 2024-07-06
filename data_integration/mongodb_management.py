import csv
from motor.motor_asyncio import AsyncIOMotorClient
from config.config import *

db = None


async def connect_to_mongodb():
    global db
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[mongodb_database]


async def save_data_to_file():
    global db

    if db is None:
        await connect_to_mongodb()

    collection = db[mongodb_collection_for_model]
    documents = collection.find()

    # Open a file for writing
    with open(
        "data_files/moodactionstats.csv", "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow(["userMoodId", "giftId", "times", "from", "type"])

        async for document in documents:
            row = (
                document["userMoodId"],
                document["giftId"],
                document["times"],
                document["from"],
                document["type"],
            )
            writer.writerow(row)
