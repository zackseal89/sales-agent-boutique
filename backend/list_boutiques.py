import asyncio
from services.supabase_service import supabase_service

async def list_boutiques():
    try:
        response = supabase_service.client.table("boutiques").select("*").execute()
        print("Boutiques:")
        for b in response.data:
            print(f"ID: {b['id']}, Name: {b['name']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_boutiques())
