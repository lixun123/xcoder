#!/usr/bin/env python3
"""
LLM Provider Abstract Base Class

This module defines the abstract base class for all LLM providers,
enabling a flexible and extensible provider architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.language_models import BaseChatModel


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs):
        """Initialize the LLM provider.

        Args:
            api_key: API key for the provider
            model: Model name to use
            **kwargs: Additional provider-specific arguments
        """
        pass

    @abstractmethod
    def generate_llm(self) -> BaseChatModel:
        """Create and return a LangChain LLM instance.

        Returns:
            BaseChatModel: A LangChain chat model instance
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name.

        Returns:
            str: Provider identifier
        """
        pass


def get_llm_provider(provider_type: str, **kwargs) -> LLMProvider:
    """Factory function to get LLM provider instance.

    Args:
        provider_type: Type of provider ('ollama', 'zhipuai')
        **kwargs: Provider initialization arguments

    Returns:
        LLMProvider: Provider instance

    Raises:
        ValueError: If provider type is not supported
    """
    from core.llm.ollama_client import OllamaClient
    from core.llm.zhipu_client import ZhipuAIClient

    providers = {
        'ollama': OllamaClient,
        'zhipuai': ZhipuAIClient,
    }

    if provider_type not in providers:
        raise ValueError(f"Unsupported LLM provider: {provider_type}. "
                         f"Supported providers: {list(providers.keys())}")

    return providers[provider_type](**kwargs)