import asyncio
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

async def apply_migration():
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("❌ SUPABASE_DB_URL not set")
        return

    migration_file = "migrations/create_checkpoints_table.sql"
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return

    with open(migration_file, "r") as f:
        sql_script = f.read()

    print(f"🔌 Connecting to database to apply migration...")
    try:
        async with await psycopg.AsyncConnection.connect(db_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql_script)
                print("✅ Migration applied successfully!")
                
    except Exception as e:
        print(f"❌ Error applying migration: {e}")

if __name__ == "__main__":
    # Fix for Windows asyncio loop
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(apply_migration())
