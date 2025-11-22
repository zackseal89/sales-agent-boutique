import os

env_path = '.env'
new_url = "SUPABASE_DB_URL=postgresql://postgres.xqaftsmseqzhlfclthyr:Ongeri74894791%40@aws-1-eu-west-1.pooler.supabase.com:6543/postgres\n"

try:
    with open(env_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith('SUPABASE_DB_URL='):
            new_lines.append(new_url)
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append(new_url)

    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ .env updated successfully")

except Exception as e:
    print(f"❌ Error updating .env: {e}")
