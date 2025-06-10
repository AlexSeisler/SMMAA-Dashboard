import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect(
            "postgresql://postgres:08%2F13%2F2022GymRat82806%21@db.lexguhkobokvdimhrsdi.supabase.co:5432/postgres?sslmode=require"
        )
        print("✅ Connected to Supabase successfully!")
        await conn.close()
    except Exception as e:
        print("❌ Connection failed:")
        print(e)

asyncio.run(test())
