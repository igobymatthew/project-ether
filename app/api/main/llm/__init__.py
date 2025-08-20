"""
LLM Connector Factory
This module provides a factory function to instantiate the correct LLM connector
based on the settings in `llm_config.yaml`.
"""

from .base import BaseLLM, BaseLLM
from .gemini import Gemini
from .lm_studio import LMStudio

def get_llm_connector() -> BaseLLM:
    """
    Factory function that reads the `llm_config.yaml` and returns an instance
    of the configured LLM connector.
    """
    config = BaseLLM.load_config()
    provider_name = config.get("active_provider")

    if not provider_name:
        raise ValueError("LLM configuration error: 'active_provider' is not set in llm_config.yaml.")

    provider_config = config.get("providers", {}).get(provider_name)
    if not provider_config:
        raise ValueError(f"LLM configuration error: No settings found for provider '{provider_name}'.")

    try:
        if provider_name == "lm-studio":
            return LMStudio(
                model=provider_config["model"],
                base_url=provider_config["base_url"],
                api_key=provider_config["api_key"],
            )
        elif provider_name == "google-gemini":
            return Gemini(
                model=provider_config["model"],
                api_key=provider_config["api_key"],
            )
        else:
            raise ValueError(f"Unsupported LLM provider specified: '{provider_name}'")
    except KeyError as e:
        raise KeyError(f"Missing required configuration key for '{provider_name}': {e}")


# Create a singleton instance of the connector to be used by the application.
# This avoids re-reading the config file on every call.
llm_connector = get_llm_connector()
