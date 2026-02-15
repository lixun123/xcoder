#!/usr/bin/env python3
"""
Base Agent Classes for CodeFixAgent

This module provides abstract base classes for different types of specialized agents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import uuid

from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver, logger

from core.agents.agent_type import AgentType
from core.utils.common import TaskItem


class BaseSubAgent(ABC):
    """Abstract base class for all specialized agents."""

    def __init__(self, llm: ChatOllama, tools: List):
        self.llm = llm
        self.tools = tools
        self.agent_type = self.get_agent_type()
        self.system_prompt = self.get_system_prompt()
        self.agent = self._create_agent()

    @abstractmethod
    def get_agent_type(self) -> AgentType:
        """Get the agent type enum."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the specialized system prompt for this agent."""
        pass

    def _create_agent(self):
        """Create the LangChain agent."""
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            # checkpointer=InMemorySaver()
        )

    def run(self, prompt: str) -> str:
        """Run the agent with a given prompt and return the response."""
        result = self.agent.invoke(
            {"messages": [HumanMessage(content=prompt)]}
        )
        for message in result["messages"]:
            pass  # Remove debug prints
        response = result["messages"][-1].content if result["messages"] else "无响应"
        return response

    def execute(self, task: TaskItem) -> Dict[str, Any]:
        """Execute a task using this agent.

        Args:
            task: The task to execute

        Returns:
            Execution result with success status and output
        """
        session_id = str(uuid.uuid4())

        # Build task message with context
        task_message = self._build_task_message(task)

        try:
            # Pre-execution hook
            pre_result = self._pre_execute(task)
            if not pre_result.get("continue", True):
                return pre_result

            # Execute the task
            result = self.agent.invoke(
                {"messages": [HumanMessage(content=task_message)]},
                {"configurable": {"thread_id": session_id}}
            )

            # Extract response
            response = result["messages"][-1].content if result["messages"] else "无响应"

            # Post-execution processing
            final_result = self._post_execute(task, response)

            return {
                "success": True,
                "result": final_result,
                "session_id": session_id
            }

        except Exception as e:
            error_result = self._handle_error(task, e)
            logger.error(f"failed to execute task {task.id} with agent {self.agent_type.value}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_details": error_result,
                "session_id": session_id
            }

    def _build_task_message(self, task: TaskItem) -> str:
        """Build the task message for the agent."""
        base_message = f"""
任务类型: {self.agent_type.value}
任务标题: {task.title}
任务描述: {task.description}
"""

        if task.context:
            context_str = self._format_context(task.context)
            base_message += f"\n上下文信息:\n{context_str}"

        base_message += "\n\n请完成这个任务，并提供详细的执行结果。"
        return base_message

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for display."""
        formatted_lines = []
        for key, value in context.items():
            if isinstance(value, str) and len(value) > 200:
                value = value[:200] + "..."
            formatted_lines.append(f"- {key}: {value}")
        return "\n".join(formatted_lines)

    def _pre_execute(self, task: TaskItem) -> Dict[str, Any]:
        """Hook called before task execution. Override in subclasses."""
        return {"continue": True}

    def _post_execute(self, task: TaskItem, response: str) -> str:
        """Hook called after task execution. Override in subclasses."""
        return response

    def _handle_error(self, task: TaskItem, error: Exception) -> Dict[str, Any]:
        """Handle execution errors. Override in subclasses."""
        return {
            "task_id": task.id,
            "agent_type": self.agent_type.value,
            "error_type": type(error).__name__
        }

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this agent provides."""
        return [tool.name if hasattr(tool, 'name') else tool.__name__ for tool in self.tools]

    def __str__(self):
        return f"{self.agent_type.value}Agent"

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.agent_type.value}, tools={len(self.tools)})"
