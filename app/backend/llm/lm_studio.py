from openai import OpenAI
from .base import BaseLLM

class LMStudio(BaseLLM):
    """LLM connector for LM Studio, which uses an OpenAI-compatible API."""

    def __init__(self, model: str, base_url: str, api_key: str):
        """
        Initializes the LM Studio connector.

        Args:
            model: The model identifier.
            base_url: The base URL of the local server (e.g., "http://localhost:1234/v1").
            api_key: The API key (often a placeholder for local models).
        """
        super().__init__(model=model, api_key=api_key)
        self.client = OpenAI(base_url=base_url, api_key=self.api_key)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generates a response using the OpenAI chat completions format."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,  # A balanced value for creative but not chaotic responses
            )
            response = completion.choices[0].message.content
            return response.strip() if response else "..."
        except Exception as e:
            print(f"ERROR: Could not connect to LM Studio. Is the server running? Details: {e}")
            # Return a fallback response so the application doesn't crash.
            return "Sorry, I'm having a little trouble thinking right now. Let's try again in a moment."
