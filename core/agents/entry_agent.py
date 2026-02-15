#!/usr/bin/env python3
"""
LangChain Agent with LLM Provider Support

This module creates a LangChain agent that supports multiple LLM providers
(Ollama, ZhipuAI, etc.) with a unified interface.
"""

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from core.llm import get_llm_provider
from core.skills.skill_middleware import SkillMiddleware
from core.tools.tool_manager import tool_manager

import os


class EntryAgent:
    """LangChain Agent with configurable LLM provider."""

    def __init__(
        self,
        provider: str = None,
        model: str = None,
        base_url: str = None,
        api_key: str = None
    ):
        """Initialize the agent.

        Args:
            provider: LLM provider type ('ollama' or 'zhipuai')
            model: Model name
            base_url: Provider base URL (for Ollama)
            api_key: API key (for cloud providers)
        """
        self.provider_type = provider or os.getenv("LLM_PROVIDER", "ollama")
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.llm = self._create_llm()
        self.tools = tool_manager.get_basic_tools()
        self.prompt = """
        你是一个智能助手，可以使用各种工具来帮助用户完成任务。
        请根据用户的需求选择合适的工具，并提供准确、有帮助的回答。
        """
        self.agent = self._create_agent()

    def _create_llm(self):
        """Create LLM instance based on configured provider."""
        provider_config = {
            "model": self.model,
            "base_url": self.base_url,
        }

        if self.api_key:
            provider_config["api_key"] = self.api_key

        client = get_llm_provider(self.provider_type, **provider_config)
        return client.generate_llm()

    def _validate_tools(self, tools_list):
        """Validate and filter tools to ensure they are proper LangChain tools."""
        validated_tools = []

        for tool in tools_list:
            try:
                # Check if it's a valid tool (has name and is callable)
                if hasattr(tool, 'name') and (callable(tool) or hasattr(tool, 'func')):
                    validated_tools.append(tool)
                else:
                    print(f"Warning: Skipping invalid tool: {tool}")
            except Exception as e:
                print(f"Warning: Error validating tool {tool}: {e}")

        return validated_tools

    def _create_agent(self):
        """Create the agent with tools."""
        # Create prompt template

        # Create agent
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
            middleware=[SkillMiddleware()]
        )

    def run(self, query: str, session_id: str = None, chat_history: list = None) -> str:
        """Run the agent with a query.

        Args:
            query: User query
            session_id: Optional session ID for memory persistence
            chat_history: Optional previous conversation history

        Returns:
            Agent response
        """

        # Add current query
        messages = []
        messages.append(HumanMessage(content=query))

        # Invoke agent with session context
        result = self.agent.invoke(
            {"messages": messages}
        )

        return result["messages"][-1]


if __name__ == "__main__":
    # Test code removed for production build
    pass
