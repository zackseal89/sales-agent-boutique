import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:20]}..." if api_key else "API Key NOT found")

if api_key:
    genai.configure(api_key=api_key)
    
    # Test with gemini-2.0-flash
    print("\nTesting gemini-2.0-flash...")
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Say 'Hello World' in JSON format: {\"message\": \"Hello World\"}")
        print(f"✅ Success! Response: {response.text}")
    except Exception as e:
        print(f"❌ Error with gemini-2.0-flash: {e}")
        
    # Test with gemini-1.5-flash (fallback)
    print("\nTesting gemini-1.5-flash...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Hello World' in JSON format: {\"message\": \"Hello World\"}")
        print(f"✅ Success! Response: {response.text}")
    except Exception as e:
        print(f"❌ Error with gemini-1.5-flash: {e}")
