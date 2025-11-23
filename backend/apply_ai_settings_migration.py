"""
Apply AI Settings Migration to Supabase
Reads and executes the 20250123000000_ai_settings.sql migration
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def apply_migration():
    """Apply the AI settings migration"""
    
    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Read migration file
    migration_path = "supabase/migrations/20250123000000_ai_settings.sql"
    
    print(f"📖 Reading migration file: {migration_path}")
    with open(migration_path, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f"📝 Migration SQL length: {len(migration_sql)} characters")
    
    # Split into individual statements (simple split by semicolon)
    # Note: This is a basic approach; for complex migrations, use a proper SQL parser
    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"🔢 Found {len(statements)} SQL statements to execute")
    
    # Execute each statement
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        # Skip comments and empty statements
        if not statement or statement.startswith('--'):
            continue
            
        try:
            print(f"\n[{i}/{len(statements)}] Executing statement...")
            print(f"Preview: {statement[:100]}...")
            
            # Execute via Supabase RPC or direct SQL execution
            # Note: Supabase Python client doesn't have direct SQL execution
            # We'll use the REST API endpoint
            result = supabase.rpc('exec_sql', {'query': statement}).execute()
            
            print(f"✅ Success")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            error_count += 1
            
            # Continue with other statements
            continue
    
    print(f"\n{'='*60}")
    print(f"Migration Summary:")
    print(f"  ✅ Successful: {success_count}")
    print(f"  ❌ Failed: {error_count}")
    print(f"{'='*60}")
    
    if error_count == 0:
        print("\n🎉 Migration completed successfully!")
    else:
        print(f"\n⚠️  Migration completed with {error_count} errors")
        print("Please review the errors above and fix manually if needed")
    
    # Verify tables were created
    print("\n🔍 Verifying new tables...")
    try:
        # Check if boutique_ai_settings exists
        result = supabase.table('boutique_ai_settings').select('*').limit(1).execute()
        print("✅ boutique_ai_settings table exists")
        
        if result.data:
            print(f"   Found {len(result.data)} default settings")
    except Exception as e:
        print(f"❌ boutique_ai_settings table check failed: {e}")
    
    try:
        # Check if prompt_version_history exists
        result = supabase.table('prompt_version_history').select('*').limit(1).execute()
        print("✅ prompt_version_history table exists")
    except Exception as e:
        print(f"❌ prompt_version_history table check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting AI Settings Migration")
    print("="*60)
    apply_migration()
