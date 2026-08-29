"""
Gemini-based structuring: transcript (mn/ja/ru) -> English translation +
title + summary + key points. One call instead of translate-then-structure
separately - fewer API round trips, one prompt to maintain.
"""

import json
import os

from google import genai

_LANGUAGE_NAMES = {
    "mn": "Mongolian",
    "ja": "Japanese",
    "ru": "Russian",
}

MODEL_ID = "gemini-3.6-flash" 


def structure_content(text: str, language_code: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    language_name = _LANGUAGE_NAMES.get(language_code, language_code)
    client = genai.Client(api_key=api_key)

    prompt = f"""Translate and structure this {language_name} oral history clip for a card-based cultural archive app.

Original transcript:
{text}

Return ONLY raw JSON (no markdown code fences, no commentary) with exactly these keys:
- "translation": a natural, fluent English translation of the full transcript
- "title": a short, engaging title, 5-10 words
- "summary": one or two sentences summarizing the content, in English
- "key_points": a list of 3-5 short factual bullet-point strings, in English

Return raw JSON only, starting with {{ and ending with }}."""

    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    raw = response.text.strip()

    # Gemini sometimes wraps JSON in ```json ... ``` even when told not to -
    # strip that defensively instead of letting json.loads() crash on it.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)