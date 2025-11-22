import asyncio
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

async def check_table():
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("❌ SUPABASE_DB_URL not set")
        return

    print(f"🔌 Connecting to database...")
    try:
        async with await psycopg.AsyncConnection.connect(db_url) as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute("SELECT to_regclass('public.checkpoints');")
                result = await cur.fetchone()
                
                if result and result['to_regclass']:
                    print("✅ Table 'checkpoints' EXISTS!")
                    
                    # Check for writes table too
                    await cur.execute("SELECT to_regclass('public.checkpoints_writes');")
                    result_writes = await cur.fetchone()
                    if result_writes and result_writes['to_regclass']:
                        print("✅ Table 'checkpoints_writes' EXISTS!")
                    else:
                        print("❌ Table 'checkpoints_writes' DOES NOT EXIST!")
                        
                else:
                    print("❌ Table 'checkpoints' DOES NOT EXIST!")

    except Exception as e:
        print(f"❌ Error connecting to DB: {e}")

if __name__ == "__main__":
    # Fix for Windows asyncio loop
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_table())
