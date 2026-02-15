
import os
from typing import Optional
from dotenv import load_dotenv
from langchain_ollama.chat_models import ChatOllama
from core.llm.base import LLMProvider

load_dotenv()


class OllamaClient(LLMProvider):
    """Ollama LLM Provider for local models."""

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize Ollama client.

        Args:
            model: Model name (defaults to qwen3:latest)
            base_url: Ollama server URL (defaults to http://localhost:11434)
            **kwargs: Additional ChatOllama arguments
        """
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:latest")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.kwargs = kwargs

    @property
    def provider_name(self) -> str:
        return "ollama"

    def generate_llm(self) -> ChatOllama:
        """Create and return a LangChain Ollama LLM instance.

        Returns:
            ChatOllama: Configured Ollama chat model
        """
        llm = ChatOllama(
            model=self.model,
            base_url=self.base_url,
            **self.kwargs
        )
        return llm

    def get_model_info(self) -> dict:
        """Get information about the current model configuration.

        Returns:
            dict: Model configuration details
        """
        return {
            "provider": self.provider_name,
            "model": self.model,
            "base_url": self.base_url
        }
