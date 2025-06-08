import openai
from typing import Dict, Any

openai.api_key = '<YOUR_API_KEY>'


def generate_caption(text: str) -> str:
    """Stub for AI-based caption or subtitle generation."""
    resp = openai.Completion.create(
        model='gpt-4o-mini',
        prompt=f"Generate a concise caption for: {text}",
        max_tokens=50
    )
    return resp.choices[0].text.strip()
