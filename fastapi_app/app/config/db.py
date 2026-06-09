from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGODB_URI, DATABASE_NAME

client: AsyncIOMotorClient | None = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGODB_URI)
    print(f"Conectado a MongoDB: {MONGODB_URI}")


async def close_db():
    global client
    if client:
        client.close()


def get_collection():
    return client[DATABASE_NAME]["esp32_lecturas"]
