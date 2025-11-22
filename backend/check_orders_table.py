import asyncio
from services.supabase_service import supabase_service

async def check_orders_table():
    print("🔍 Checking 'orders' table structure...")
    
    try:
        # Try to select one row to see if table exists and get keys
        response = supabase_service.client.table("orders").select("*").limit(1).execute()
        
        print("✅ Table 'orders' exists!")
        if response.data:
            print("Columns found in existing data:")
            print(response.data[0].keys())
        else:
            print("Table is empty, but exists.")
            
            # Try to insert a dummy row to fail and see columns in error, or just assume standard
            # For now, we just confirm existence.
            
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        if "404" in str(e) or "relation \"orders\" does not exist" in str(e):
            print("Table likely does not exist.")

if __name__ == "__main__":
    asyncio.run(check_orders_table())
