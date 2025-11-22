import os

env_path = '.env'
new_url = "MPESA_CALLBACK_URL=https://0dd6a69323c9.ngrok-free.app/webhook/paylink/payment\n"

try:
    with open(env_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith('MPESA_CALLBACK_URL='):
            new_lines.append(new_url)
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        new_lines.append(new_url)

    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ .env updated successfully: MPESA_CALLBACK_URL set")

except Exception as e:
    print(f"❌ Error updating .env: {e}")
