# src/llm_processor.py

import os
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMProcessor:
    """
    Handles interaction with the LLM API.
    Converts raw text into a podcast-style script.
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=api_key)

    def _extract_text(self, content):
        """
        Ensures we always return a clean string, even if the API returns a list.
        """
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            # New SDK sometimes returns [{"type": "text", "text": "..."}]
            parts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
            return "\n".join(parts).strip()

        return str(content).strip()

    def generate_podcast_script(self, data: Dict[str, str]) -> str:
        """
        Takes standardized data dict and returns a podcast-ready script.
        """

        raw_content = data.get("raw_content", "")
        if not raw_content:
            raise ValueError("No content provided to LLMProcessor.")

        system_prompt = (
            "You are a podcast script writer. "
            "Turn the provided text into a short, engaging 3–4 minute podcast script "
            "with a friendly intro, clear structure, and a smooth outro."
        )

        user_prompt = (
            "Here is the source content to adapt into a podcast script:\n\n"
            f"{raw_content}"
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        # Extract content safely
        content = response.choices[0].message.content
        script = self._extract_text(content)

        return script