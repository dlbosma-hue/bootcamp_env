# src/tts_generator.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class TTSGenerator:
    """
    Handles text-to-speech generation using the latest OpenAI TTS API.
    Produces an MP3 file from a text script.
    """

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in .env file.")
        self.client = OpenAI(api_key=api_key)

    def text_to_speech(self, text: str, output_path: str = "podcast_output.mp3"):
        """
        Converts text into speech and saves it as an MP3 file.
        Returns the file path.
        """

        if not text or not text.strip():
            raise ValueError("No text provided for TTS generation.")

        # Generate audio using OpenAI TTS
        response = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text
        )

        # Save binary audio to file
        with open(output_path, "wb") as f:
            f.write(response.read())

        return output_path