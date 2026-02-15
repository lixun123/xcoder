"""
Tool manager for organizing and providing tools to different types of agents
"""

from typing import List

from .file_read import read_file, list_files, find_files
from .file_write import write_file
from .search_tools import web_search
from .system_tools import execute_bash_command
from .file_edit import edit_file, read_file_with_lines
from core.agents.base_sub_agent import AgentType
from core.mcp.client import mcp_client


class ToolManager:
    """Manages all available tools for different types of agents."""

    def __init__(self):
        """Initialize the tool manager."""
        self._basic_tools = [
            read_file,
            list_files,
            find_files,
            read_file_with_lines,
            write_file,
            edit_file,
            web_search,
            execute_bash_command
        ]

        self.mcp_tools = self._load_mcp_tools()

        self._agent_tool_mapping = {
            AgentType.ANALYZER: [
                read_file,
                list_files,
                find_files,
                web_search,
            ],
            AgentType.PLANNER: [
                read_file,
                list_files,
                find_files,
                web_search,
            ],
            AgentType.CODER: [
                read_file,
                list_files,
                find_files,
                read_file_with_lines,
                write_file,
                edit_file,
                execute_bash_command,
            ],
            AgentType.INTENT: [
                read_file,
                list_files,
                find_files,
                # Minimal tools for lightweight classification
            ],
            AgentType.QUICKFIX: [
                read_file,
                list_files,
                find_files,
                read_file_with_lines,
                write_file,
                edit_file,
                execute_bash_command,
                # Full tool access for integrated analysis and repair
            ]
        }

    def get_basic_tools(self) -> List:
        """Get the basic tools available to any agent.

        Returns:
            List of basic tools (file operations, web search, bash commands)
        """
        return self._basic_tools

    def get_tools_for_agent(self, agent_type: AgentType) -> List:
        """Get specialized tools for a specific agent type.

        Args:
            agent_type: The type of agent requesting tools

        Returns:
            List of tools appropriate for the agent type
        """
        base_tools = self._agent_tool_mapping.get(agent_type, self._basic_tools)
        mcp_tools = self._filter_mcp_tools_for_agent(agent_type)
        return base_tools + mcp_tools


    def _load_mcp_tools(self):
        """Load MCP tools using our MCP client.

        Returns:
            List of MCP tools
        """
        try:
            if not mcp_client.is_available():
                mcp_client.initialize()
            return []
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug(f"MCP tools not available: {e}")
            return []

    def _filter_mcp_tools_for_agent(self, agent_type: AgentType) -> List:
        """Filter MCP tools based on agent type.

        Args:
            agent_type: The type of agent requesting tools

        Returns:
            List of MCP tools appropriate for the agent type
        """
        return self.mcp_tools


tool_manager = ToolManager()
