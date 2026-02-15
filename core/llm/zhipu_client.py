#!/usr/bin/env python3
"""
ZhipuAI Client for GLM Models

This module provides integration with ZhipuAI's GLM series models,
including GLM-4-Flash and other variants.
"""

import os
import warnings
from typing import Optional
from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from core.llm.base import LLMProvider

# 过滤JWT密钥长度警告
warnings.filterwarnings("ignore", message=".*HMAC key is .* bytes long.*", category=Warning)

load_dotenv()


class ZhipuAIClient(LLMProvider):
    """ZhipuAI LLM Provider for GLM models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """Initialize ZhipuAI client.

        Args:
            api_key: ZhipuAI API key (defaults to ZHIPUAI_API_KEY env var)
            model: Model name (defaults to GLM-4-Flash)
            base_url: API base URL (optional)
            **kwargs: Additional ChatZhipuAI arguments
        """
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        self.model = model or os.getenv("ZHIPUAI_MODEL", "glm-4.7-flash")
        self.base_url = base_url

        if not self.api_key:
            raise ValueError("ZhipuAI API key is required. "
                             "Set ZHIPUAI_API_KEY environment variable or pass api_key parameter.")

        self.kwargs = kwargs

    @property
    def provider_name(self) -> str:
        return "zhipuai"

    def generate_llm(self) -> ChatZhipuAI:
        """Create and return a LangChain ZhipuAI LLM instance.

        Returns:
            ChatZhipuAI: Configured ZhipuAI chat model
        """
        llm = ChatZhipuAI(
            api_key=self.api_key,
            model=self.model,
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
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key)
        }
