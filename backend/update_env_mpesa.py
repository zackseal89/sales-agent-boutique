"""
Update .env file with M-Pesa credentials
"""

import os
from pathlib import Path

# Read current .env
env_path = Path(__file__).parent / ".env"
with open(env_path, 'r') as f:
    lines = f.readlines()

# M-Pesa encrypted initiator password (sandbox)
encrypted_password = "AUZ/rSrAnQZl3N7fRDvrHHIizRaedkhv77hOxlj0kHXVFfgqfrxLwFnsWxpQ5931p0Z3Icp4tVTNmMbkFv+FN+/lLOVPgL1pGEAqBk8RpS4lfwlO4tw7/PJhDkYOwa2kmE6Zgus78DUKjwpcWSoKcUmWM3GeL092RkcQkzhNdZEdeW6Jp/YVrPF9DibQwQAwRGG6Wui/h8dLtaH78Zr7G2QVvX/H+U7ii61hvzBjnpwX475HsG1oSrBzrJE48mloCjxrwv+RB0HoFC8xYHLCr0DFecC31rG0j/Yqb0sHbPEtBJG+AHLGkr779v0MSx7V+WjZ1aIQNNGO7A/h8vleuQ=="

# Ngrok URL
ngrok_url = "https://4c040e3c9ac8.ngrok-free.app"

# Update lines
updated_lines = []
for line in lines:
    if line.startswith("MPESA_PASSKEY="):
        updated_lines.append(f"MPESA_PASSKEY={encrypted_password}\n")
    elif line.startswith("MPESA_CALLBACK_URL="):
        updated_lines.append(f"MPESA_CALLBACK_URL={ngrok_url}/webhook/paylink/payment\n")
    else:
        updated_lines.append(line)

# Write back
with open(env_path, 'w') as f:
    f.writelines(updated_lines)

print("✅ Updated .env with M-Pesa credentials")
print(f"   - MPESA_PASSKEY: {encrypted_password[:50]}...")
print(f"   - MPESA_CALLBACK_URL: {ngrok_url}/webhook/paylink/payment")
