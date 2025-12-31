# from contextlib import asynccontextmanager
# from logging import info

# from main import MONGO_URL @asynccontextmanager
# from fastapi import FastAPI
# from motor import AsyncIOMotorClient

# async def db_lifespan(app: FastAPI):
#     # Startup
#     app.mongodb_client = AsyncIOMotorClient(MONGO_URL)
#     app.database = app.mongodb_client.get_default_database()
#     ping_response = await app.database.command("ping")
#     if int(ping_response["ok"]) != 1:
#         raise Exception("Problem connecting to database cluster.")
#     else:
#         info("Connected to database cluster.")
    
#     yield

#     # Shutdown
#     app.mongodb_client.close()


# app: FastAPI = FastAPI(lifespan=db_lifespan)