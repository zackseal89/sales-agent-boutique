import os
import asyncio
import psycopg
from dotenv import load_dotenv

load_dotenv()

import sys
import socket
from urllib.parse import urlparse

# Fix for Windows ProactorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test_connection():
    db_url = os.getenv("SUPABASE_DB_URL")
    
    if not db_url:
        print("❌ SUPABASE_DB_URL is not set or empty")
        return

    print(f"🔍 Raw URL repr: {repr(db_url)}")
    
    try:
        parsed = urlparse(db_url)
        host = parsed.hostname
        port = parsed.port
        print(f"🔍 Parsed Host: '{host}'")
        print(f"🔍 Parsed Port: {port}")
        
        if host:
            print(f"🔍 Attempting to resolve {host}...")
            ip = socket.gethostbyname(host)
            print(f"✅ Resolved to IP: {ip}")
        else:
            print("❌ Could not parse hostname from URL")
    except Exception as e:
        print(f"❌ DNS Resolution failed: {e}")

    # Mask password for printing
    masked_url = db_url
    if "@" in db_url:
        # Split from the right to handle @ in password
        part1, part2 = db_url.rsplit("@", 1)
        # part1 is user:pass, part2 is host:port/db
        if ":" in part1:
            user = part1.split(":")[0]
            masked_url = f"{user}:****@{part2}"
        else:
            masked_url = f"****@{part2}"
    
    print(f"Testing connection to: {masked_url}")
    
    try:
        async with await psycopg.AsyncConnection.connect(db_url) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute("SELECT version()")
                result = await acur.fetchone()
                print(f"✅ Connection successful! DB Version: {result[0]}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
