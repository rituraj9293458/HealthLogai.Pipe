from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os


load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URI")
)

db = client["health_analysis"]

daily_analysis = db["daily_analysis"]


def save_daily_analysis(steps, screen, food):

    document = {
        "date": datetime.now(),
        "steps": steps,
        "screen": screen,
        "food": food
    }

    result = daily_analysis.insert_one(document)

    # Get the document we just inserted
    saved_document = daily_analysis.find_one(
        {"_id": result.inserted_id}
    )

    saved_document["_id"] = str(saved_document["_id"])

    return saved_document


def dbsave(state):
    steps = state.get("steps", "")
    screen = state.get("screen", "")
    food = state.get("food", "")

    saved_document = save_daily_analysis(
        steps=steps,
        screen=screen,
        food=food
    )

    return {
        "db_data": [saved_document]
    }