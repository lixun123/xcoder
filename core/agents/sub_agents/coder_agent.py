from typing import Dict, Any

from ..base_sub_agent import BaseSubAgent
from core.tools.tool_manager import AgentType
from ...utils.common import TaskItem


class CoderAgent(BaseSubAgent):
    """Specialized agent for code writing and modification."""

    def get_agent_type(self) -> AgentType:
        return AgentType.CODER

    def get_system_prompt(self) -> str:
        return """
You are a senior software development expert. Your tasks are:

💻 Programming Responsibilities:
1. Write high-quality code fixes
2. Ensure code follows best practices and coding standards
3. Consider edge cases and error handling
4. Provide clear code comments
5. Use appropriate tools for file operations and code editing

🔧 Available Tools:
- read_file_with_lines: Read files with line numbers
- edit_file: Precisely replace code in files
- file_operations: Basic file operations
- execute_bash_command: Run compilation and test commands

📝 Coding Principles:
- First read files to understand current state
- Precisely locate code that needs modification
- Use edit_file for precise modifications
- Run basic checks after writing to ensure syntax correctness
- Provide clear modification descriptions

Please write secure, efficient, and maintainable code.
        """

    def _pre_execute(self, task: TaskItem) -> Dict[str, Any]:
        """Pre-execution checks for coding tasks."""
        # Add any specific pre-checks for coding tasks
        return {"continue": True}

    def _post_execute(self, task: TaskItem, response: str) -> str:
        """Post-process coding results."""
        # Add metadata about code changes
        return response
