#!/usr/bin/env python3
"""
LLM Provider Package

This package provides flexible LLM provider support with a unified interface.
Supported providers:
- ollama: Local Ollama models
- zhipuai: ZhipuAI GLM models
"""

from core.llm.base import LLMProvider, get_llm_provider
from core.llm.ollama_client import OllamaClient
from core.llm.zhipu_client import ZhipuAIClient

__all__ = [
    'LLMProvider',
    'get_llm_provider',
    'OllamaClient',
    'ZhipuAIClient',
]


def get_provider_type() -> str:
    """Get configured provider type from environment.

    Returns:
        str: Provider type ('ollama' or 'zhipuai')
    """
    import os
    return os.getenv("LLM_PROVIDER", "ollama")


def create_llm(provider_type: str = None, **kwargs):
    """Create an LLM instance with the specified or configured provider.

    Args:
        provider_type: Provider type (uses LLM_PROVIDER env var if not specified)
        **kwargs: Provider-specific arguments

    Returns:
        BaseChatModel: LangChain chat model instance
    """
    provider = get_llm_provider(provider_type or get_provider_type(), **kwargs)
    return provider.generate_llm()