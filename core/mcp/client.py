"""
MCP Client implementation for XCoder using MultiServerMCPClient
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
import json
import os
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client using LangChain's MultiServerMCPClient."""

    def __init__(self):
        """Initialize the MCP client."""
        self.client = None
        self.is_mcp_available = False
        self.config = None
        self.config_path = Path(__file__).parent / "mcp_config.json"

    def load_config(self) -> Dict[str, Any]:
        """Load MCP configuration from config file.

        Returns:
            Configuration dictionary
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"MCP config file not found: {self.config_path}")
                return {"servers": {}, "default_servers": [], "capabilities": {}}

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            logger.info(f"Loaded MCP config with {len(config.get('servers', {}))} servers")
            return config

        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            return {"servers": {}, "default_servers": [], "capabilities": {}}

    def _build_server_config(self, server_name: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build server configuration for MultiServerMCPClient.

        Args:
            server_name: Name of the server
            server_config: Server configuration from config file

        Returns:
            Server configuration dictionary for MultiServerMCPClient
        """
        transport = server_config.get("transport", "stdio")

        if transport == "http":
            return {
                "transport": "http",
                "url": server_config["url"]
            }
        elif transport == "stdio":
            config = {
                "transport": "stdio",
                "command": server_config.get("command", "npx"),
                "args": server_config.get("args", [])
            }

            # Add environment variables if specified
            if "env" in server_config:
                config["env"] = server_config["env"]

            return config
        else:
            logger.error(f"Unsupported transport type: {transport} for server {server_name}")
            return None

    def initialize(self) -> bool:
        """Initialize MCP client with MultiServerMCPClient from config file.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load configuration
            self.config = self.load_config()
            servers_config = self.config.get("servers", {})

            if not servers_config:
                logger.warning("No MCP servers configured")
                self.is_mcp_available = False
                return False

            # Build server configurations for MultiServerMCPClient
            client_servers = {}

            for server_name in self.config:

                server_config = servers_config[server_name]
                client_config = self._build_server_config(server_name, server_config)

                if client_config:
                    client_servers[server_name] = client_config
                    logger.info(f"Configured MCP server: {server_name} ({server_config.get('transport', 'stdio')})")

            if not client_servers:
                logger.warning("No valid MCP server configurations found")
                self.is_mcp_available = False
                return False

            # Initialize MultiServerMCPClient
            self.client = MultiServerMCPClient(client_servers)
            self.is_mcp_available = True

            logger.info(f"MCP client initialized with {len(client_servers)} servers")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            self.is_mcp_available = False
            return False

    def is_available(self) -> bool:
        """Check if MCP framework is available.

        Returns:
            True if MCP is available, False otherwise
        """
        return self.is_mcp_available

    async def get_tools(self) -> List[Any]:
        """Get available tools from configured servers using MultiServerMCPClient.

        Returns:
            List of available tools
        """
        if not self.client:
            return []

        try:
            async with self.client:
                mcp_tools = await self.client.get_tools()
                logger.info(f"Retrieved {len(mcp_tools)} tools from MCP servers")
                return mcp_tools
        except Exception as e:
            logger.error(f"Failed to get MCP tools: {e}")
            return []


# Global MCP client instance
mcp_client = MCPClient()
