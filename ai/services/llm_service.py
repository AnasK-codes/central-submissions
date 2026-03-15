"""
ai/services/llm_service.py

Shared Groq LLM client and response generation.
Extracted from check_answers.py to avoid duplication.
"""
from groq import Groq
from ai.config import ai_settings

_client = None


def _get_client():
    """Lazy-initialize the Groq client."""
    global _client
    if _client is None:
        _client = Groq(api_key=ai_settings.GROQ_API_KEY)
    return _client


def generate_response(prompt: str, ltm=None) -> str:
    """
    Send a prompt to the Groq LLM and return the text response.

    Args:
        prompt: The user-facing prompt to send.
        ltm: Optional long-term memory context to include in the system message.

    Returns:
        The assistant's reply as a string, or an error message on failure.
    """
    try:
        system_text = (
            "You are an AI assistant. "
            "Follow instructions exactly. "
            "If asked for JSON, return ONLY valid JSON."
        )

        if ltm:
            system_text += f" Memory: {ltm}"

        client = _get_client()
        chat_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"
