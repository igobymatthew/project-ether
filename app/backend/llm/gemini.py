import os
import google.generativeai as genai
from .base import BaseLLM

class Gemini(BaseLLM):
    """LLM connector for the Google Gemini API."""

    def __init__(self, model: str, api_key: str):
        """
        Initializes the Gemini connector.

        Args:
            model: The Gemini model to use.
            api_key: The Google AI API key.
        """
        # For security, prioritize environment variables over config file keys.
        resolved_api_key = os.getenv("GOOGLE_API_KEY") or api_key
        if not resolved_api_key or resolved_api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError(
                "Google Gemini API key not found. "
                "Please set it in llm_config.yaml or as a GOOGLE_API_KEY environment variable."
            )

        super().__init__(model=model, api_key=resolved_api_key)

        try:
            genai.configure(api_key=self.api_key)
            self.model_instance = genai.GenerativeModel(self.model)
        except Exception as e:
            print(f"ERROR: Failed to configure Google Gemini. Check your API key. Details: {e}")
            raise

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a response from Gemini.

        Note: The Gemini API prefers a combined prompt rather than a separate "system" role.
        """
        # Combine the system and user prompts into a single prompt for Gemini.
        full_prompt = f"{system_prompt}\n\n---\n\nUser query: \"{user_prompt}\""

        try:
            response = self.model_instance.generate_content(full_prompt)
            # Ensure response.text is not None before stripping
            return response.text.strip() if response.text else "..."
        except Exception as e:
            print(f"ERROR: Google Gemini request failed. Details: {e}")
            return "Sorry, my thoughts are a bit scrambled right now. Could you repeat that?"
