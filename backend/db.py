import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
db_pool = None

async def init_db():
    global db_pool
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("✅ Connected to Supabase PostgreSQL successfully.")
    except Exception as e:
        print("❌ Failed to connect to database:", str(e))
        raise

async def fetch_all(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def fetch_one(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def execute(query: str, *args):
    async with db_pool.acquire() as conn:
        return await conn.execute(query, *args)
