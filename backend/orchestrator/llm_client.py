import os
import json
import logging
import asyncio
import google.generativeai as genai
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("⚠️ GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")

async def generate_response(prompt: str, image_url: str = None) -> Dict[str, Any]:
    """
    Generate structured response from Gemini LLM.
    Enforces JSON schema for deterministic parsing.
    """
    # Mock flag
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    if use_mock:
        logger.info("🔧 Mock LLM enabled – returning static response")
        return {
            "reply_text": "Hello! I'm a mock Gemini response. How can I assist you today?",
            "actions": [],
            "intent": "mock_greeting",
            "entities": {}
        }

    try:
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-2.0-flash")  # stable model

        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7,
        )

        parts = [prompt]

        def _sync_generate():
            return model.generate_content(
                contents=parts,
                generation_config=generation_config,
            )

        logger.info("🔄 Calling Gemini generate_content via asyncio.to_thread...")
        response = await asyncio.to_thread(_sync_generate)
        logger.info(f"✅ LLM response received: {response}")

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
        print(error_msg)
        import traceback
        traceback_msg = traceback.format_exc()
        logger.error(f"Traceback: {traceback_msg}")
        print(f"Traceback: {traceback_msg}")
        return _fallback_response()

def _fallback_response() -> Dict[str, Any]:
    """Return safe fallback if LLM fails"""
    return {
        "reply_text": "I'm having trouble connecting to my brain right now. 🧠 Please try again in a moment!",
        "actions": [],
        "intent": "error",
        "entities": {}
    }
