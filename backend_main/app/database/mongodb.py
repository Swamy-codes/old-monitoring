import os
import urllib.parse
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("MONGO_URL is not set in the environment variables")

parsed_url = urllib.parse.urlparse(MONGO_URL)
username = urllib.parse.quote_plus(parsed_url.username) if parsed_url.username else ''
password = urllib.parse.quote_plus(parsed_url.password) if parsed_url.password else ''
host = parsed_url.hostname
port = parsed_url.port
auth_source = urllib.parse.parse_qs(parsed_url.query).get('authSource', ['admin'])[0]

# Reconstruct the MongoDB URI
MONGO_URI = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
client = AsyncIOMotorClient(MONGO_URI)
db = client["EFORCAST_CMTI"]
collection = db["Elno_SensorDataActive"]

async def startup_mongodb(app):
    app.state.mongodb_client = client
    app.state.mongodb_db = db
    app.state.mongodb_collection = collection

async def shutdown_mongodb(app):
    client.close()

def get_mongodb_db(app):
    return app.state.mongodb_db

def get_mongodb_collection(app):
    return app.state.mongodb_collection
