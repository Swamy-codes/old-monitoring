import asyncpg
import os
from dotenv import load_dotenv
from fastapi import Request
load_dotenv()

async def startup_postgres(app):

#    create a pool of database connections with parameters fetched from environment variables.
    app.state.postgres_pool = await asyncpg.create_pool(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB'),
        # min and max number of connections in the pool.
        min_size=1,
        max_size=20
    )

async def shutdown_postgres(app):
    await app.state.postgres_pool.close()

async def get_postgres_pool(app):
    # retuerns current connection pool
    return app.state.postgres_pool
async def get_postgres_pool_1(request: Request):
    return request.app.state.postgres_pool