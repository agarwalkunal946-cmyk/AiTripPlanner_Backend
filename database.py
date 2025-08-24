import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.trip_planner
user_collection = database.get_collection("users")
trip_collection = database.get_collection("trips")
chat_collection = database.get_collection("chat_messages")

def get_database():
    """Get the database instance"""
    return database