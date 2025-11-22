"""
Add MPESA_BASE_URL to .env
"""

import os
from pathlib import Path

# Read current .env
env_path = Path(__file__).parent / ".env"
with open(env_path, 'r') as f:
    lines = f.readlines()

# Check if MPESA_BASE_URL exists
has_base_url = any(line.startswith("MPESA_BASE_URL=") for line in lines)

if not has_base_url:
    # Find MPESA_ENVIRONMENT line and add BASE_URL after it
    updated_lines = []
    for i, line in enumerate(lines):
        updated_lines.append(line)
        if line.startswith("MPESA_ENVIRONMENT="):
            updated_lines.append("MPESA_BASE_URL=https://sandbox.safaricom.co.ke\n")
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Added MPESA_BASE_URL to .env")
else:
    print("ℹ️  MPESA_BASE_URL already exists")
