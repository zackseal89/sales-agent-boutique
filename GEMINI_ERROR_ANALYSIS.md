# Gemini LLM Integration Error - Complete Analysis

## Problem Summary
WhatsApp messages arrive successfully at the backend, but the Gemini LLM call fails, returning a fallback error: "I'm having trouble connecting to my brain right now. 🧠"

## System Architecture (Working Parts)
✅ Twilio WhatsApp → Webhook arrives
✅ Ngrok tunnel → Forwards to localhost:8000
✅ FastAPI backend → Receives POST /webhook/whatsapp
✅ Orchestrator → Processes message
✅ WhatsApp response → Sends back successfully

❌ **ONLY FAILING PART**: Gemini LLM API call in `llm_client.py`

## Exact Error Location

**File**: `c:\Users\user\sales agent v2 botique\backend\orchestrator\llm_client.py`

**Function**: `generate_response()` (line 14-62)

**Failing Line**: Approximately line 38 - `response = model.generate_content(...)`

## Current Code (llm_client.py)

```python
import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configure Gemini (will be done inside async function)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("⚠️ GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")

async def generate_response(prompt: str, image_url: str = None) -> Dict[str, Any]:
    """
    Generate structured response from Gemini LLM.
    Enforces JSON schema for deterministic parsing.
    """
    try:
        # Configure Gemini API (inside async context)
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        
        model = genai.GenerativeModel('gemini-exp-1206')  # Currently trying this model
        
        # Define generation config for JSON mode
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7,
        )
        
        # Prepare content parts
        parts = [prompt]
        
        # Use synchronous call (async has event loop issues with FastAPI)
        response = model.generate_content(  # ← THIS LINE FAILS
            contents=parts,
            generation_config=generation_config
        )
        
        # Parse JSON response
        response_text = response.text
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"❌ Failed to parse LLM JSON: {response_text}")
            if "```json" in response_text:
                clean_text = response_text.split("```json")[1].split("```")[0].strip()
                return json.loads(clean_text)
            return _fallback_response()
            
    except Exception as e:
        error_msg = f"❌ LLM Generation failed: {str(e)}"
        logger.error(error_msg)
        print(error_msg)  # Force console output
        import traceback
        traceback_msg = traceback.format_exc()
        logger.error(f"Traceback: {traceback_msg}")
        print(f"Traceback: {traceback_msg}")  # Force console output
        return _fallback_response()

def _fallback_response() -> Dict[str, Any]:
    """Return safe fallback if LLM fails"""
    return {
        "reply_text": "I'm having trouble connecting to my brain right now. 🧠 Please try again in a moment!",
        "actions": [],
        "intent": "error",
        "entities": {}
    }
```

## Environment Configuration

**File**: `c:\Users\user\sales agent v2 botique\.env`

```env
GOOGLE_API_KEY=AIzaSyCO3EeQoN5oIRnMhpv9DwYq0ofH_0gVZns
GEMINI_API_KEY=AIzaSyCO3EeQoN5oIRnMhpv9DwYq0ofH_0gVZns
```

## What We've Tried

1. ✅ **API Key**: Verified loaded correctly (`AIzaSyCO3EeQoN5oIRnM...`)
2. ✅ **Standalone Test**: Created `test_gemini.py` - **WORKS PERFECTLY** with `gemini-2.0-flash` synchronously
3. ❌ **Model Names Tried**:
   - `gemini-2.0-flash-exp` → Failed
   - `gemini-2.0-flash` → Failed
   - `gemini-1.5-pro` → Failed
   - `gemini-exp-1206` → Currently trying (likely failing)
4. ✅ **Async → Sync**: Changed from `generate_content_async()` to `generate_content()`
5. ✅ **Event Loop Fix**: Moved `genai.configure()` inside async function

## Test Script That WORKS

**File**: `c:\Users\user\sales agent v2 botique\test_gemini.py`

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('.env')
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content("Say 'Hello World' in JSON format")
print(f"✅ Success! Response: {response.text}")
# Output: ✅ Success! Response: ```json\n{"message": "Hello World"}\n```
```

## The Mystery

- **Standalone script**: Works perfectly ✅
- **Inside FastAPI orchestrator**: Fails ❌
- **Same API key**: Yes
- **Same model call**: Yes
- **Same library version**: Yes

## Suspected Issues

1. **FastAPI async context** - Event loop conflict
2. **Missing error output** - Print statements not showing in console
3. **Model availability** - API key might not have access to these models
4. **Request context** - Something about the FastAPI request context breaks the call

## What We Need

The **actual error message** from the exception. The print statements should show it, but we're not seeing console output.

## Request for ChatGPT

Please analyze:
1. Why would `generate_content()` work in a standalone script but fail in FastAPI?
2. What's the correct model name for Gemini 2.5 Pro in the API?
3. How to properly integrate Google Generative AI with FastAPI async functions?
4. Why aren't the print() statements showing in uvicorn console output?

## Dependencies

```
google-generativeai==0.8.3
fastapi==0.115.6
uvicorn==0.34.0
python-dotenv==1.0.1
```

## FastAPI Context

The `generate_response()` function is called from:
- `backend/orchestrator/message_handler.py` (line 64)
- Inside an async function `handle_whatsapp_message()`
- Which is called from FastAPI route handler in `backend/api/webhooks.py`
