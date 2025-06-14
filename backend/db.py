import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool, shared across routes
db_pool = None

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=3,
        timeout=30
    )

async def fetch_all(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def fetch_one(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def execute(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.execute(query, *args)