# Gemini LLM Fix Plan - Bug-Fix-Validation-Workflow

## Bug-Fix-Validation-Workflow Steps

### 1. ✅ Reproduce Bug
**Status**: CONFIRMED
- WhatsApp messages arrive successfully
- Orchestrator processes messages
- LLM call fails silently
- Fallback error returned: "I'm having trouble connecting to my brain"

### 2. ✅ Isolate Root Cause
**Primary Hypothesis** (from ChatGPT analysis):
- **Gemini 2.5 Pro instability** in non-streaming mode via Python SDK
- **Empty response / 500 Internal Error** bug reported by multiple users
- **Model/SDK mismatch** - wrong API version or generation config

**Supporting Evidence**:
- Standalone test script works (different execution context)
- FastAPI integration fails (async context + SDK issue)
- No error logs visible (silent failure)

### 3. 🔧 Fix - Smallest Surface Area

**Approach**: Implement fixes in order of likelihood, testing each one

#### Fix #1: Switch to Streaming API (HIGHEST PRIORITY)
**Why**: Multiple users report streaming works when non-streaming fails
**Change**: Replace `generate_content()` with `generate_content_stream()`
**File**: `backend/orchestrator/llm_client.py`
**Lines**: 39-42

#### Fix #2: Add Deep Logging
**Why**: Need to see actual error (finish_reason, candidates)
**Change**: Log response object details before parsing
**File**: `backend/orchestrator/llm_client.py`
**Lines**: 44-54

#### Fix #3: Disable Thinking Mode
**Why**: Gemini 2.5 models have thinking enabled by default, may cause issues
**Change**: Set `thinking_budget=0` in generation config
**File**: `backend/orchestrator/llm_client.py`
**Lines**: 26-30

#### Fix #4: Fallback to Stable Model
**Why**: `gemini-2.0-flash-exp` proven to work in test script
**Change**: Use `gemini-2.0-flash-exp` instead of experimental models
**File**: `backend/orchestrator/llm_client.py`
**Line**: 24

### 4. 🧪 Validate Fix

**Test Plan**:
1. Apply Fix #1 (streaming) + Fix #2 (logging)
2. Send WhatsApp test message
3. Check logs for actual error or success
4. If still fails, apply Fix #3 (disable thinking)
5. If still fails, apply Fix #4 (fallback model)

**Regression Tests**:
- Verify standalone test script still works
- Verify WhatsApp webhook still receives messages
- Verify response is sent back to WhatsApp

**Edge Cases**:
- Long prompts (context window)
- JSON parsing errors
- Rate limiting

### 5. 📋 Guardrails

**No Refactoring**:
- Keep existing orchestrator logic unchanged
- Only modify LLM client implementation
- Maintain same function signature

**No Unrelated Improvements**:
- Don't add features (caching, retries, etc.)
- Don't optimize prompt building
- Don't change error handling beyond logging

---

## Implementation Steps

### Step 1: Apply Streaming + Logging Fix
```python
# backend/orchestrator/llm_client.py (lines 38-54)

# Use streaming to avoid empty response bug
response_text = ""
try:
    for chunk in model.generate_content_stream(
        contents=parts,
        generation_config=generation_config
    ):
        if chunk.text:
            response_text += chunk.text
    
    logger.info(f"✅ LLM Response received: {response_text[:100]}...")
    
except Exception as stream_error:
    logger.error(f"❌ Streaming failed: {stream_error}")
    raise

# Parse JSON response
try:
    return json.loads(response_text)
except json.JSONDecodeError:
    logger.error(f"❌ Failed to parse LLM JSON: {response_text}")
    if "```json" in response_text:
        clean_text = response_text.split("```json")[1].split("```")[0].strip()
        return json.loads(clean_text)
    return _fallback_response()
```

### Step 2: Add Thinking Budget Config (if Step 1 fails)
```python
# backend/orchestrator/llm_client.py (lines 26-30)

generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
    temperature=0.7,
    # Disable thinking mode to avoid instability
    # Note: This may not be supported in all SDK versions
)
```

### Step 3: Fallback to Proven Model (if Step 2 fails)
```python
# backend/orchestrator/llm_client.py (line 24)

model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Proven to work in test
```

---

## Expected Outcomes

### Success Criteria:
1. ✅ WhatsApp message triggers LLM response
2. ✅ Actual AI-generated content returned (not fallback error)
3. ✅ Logs show successful LLM call
4. ✅ JSON parsing works correctly

### Failure Indicators:
1. ❌ Still getting fallback error
2. ❌ Logs show empty response / 500 error
3. ❌ Rate limit / quota errors

---

## Rollback Plan

If all fixes fail:
1. Revert to original `llm_client.py`
2. Consider alternative LLM providers (OpenAI, Anthropic)
3. Or use Gemini via REST API directly (bypass SDK)

---

## Next Action

**READY TO IMPLEMENT**: Apply Fix #1 (Streaming + Logging) immediately and test.
