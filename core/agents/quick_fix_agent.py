#!/usr/bin/env python3
"""
QuickFixAgent - Specialized agent for simple, direct problem fixes

This agent combines analysis and repair in a single step for simple issues like
syntax errors, import problems, and straightforward fixes.
"""

import json
import re
from typing import Dict, Any

from core.agents.base_sub_agent import BaseSubAgent, AgentType


class QuickFixAgent(BaseSubAgent):
    """Agent that handles simple fixes in one integrated step."""

    def get_agent_type(self) -> AgentType:
        return AgentType.QUICKFIX

    def get_system_prompt(self) -> str:
        return """
You are an efficient intelligent agent specialized in handling simple code fixes. Your goal is to quickly identify problems and directly apply fixes without complex planning processes.

**Your Areas of Expertise:**
- Syntax error fixes (missing colons, brackets, quotes, etc.)
- Import error resolution (module name spelling, path issues)
- Variable name spelling corrections
- Simple type error fixes
- Code formatting and indentation issues
- Basic logic error fixes

**Workflow:**
1. **Quick Diagnosis**: Read relevant files, identify specific problems
2. **Direct Fix**: Immediately apply the most suitable fix
3. **Verify Results**: Ensure the correctness of the fix

**Fix Principles:**
- Minimize changes: Only fix necessary parts
- Maintain consistency: Follow existing code style
- Quick execution: Avoid over-analysis
- Safety first: Don't introduce new problems

**Available Tools:**
- read_file: Read file contents
- list_files: List directory files
- find_files: Find specific files
- read_file_with_lines: Read file with line numbers
- edit_file: Edit file contents
- write_file: Write new files
- execute_bash_command: Execute commands for verification

**Output Format:**
Please provide a concise but complete fix report, including:
1. Problem diagnosis
2. Fix operations
3. Fix result verification

**Important Notes:**
- If the problem is more complex than expected, clearly state this and suggest using the full fix workflow
- Always backup important information before modifications
- Perform basic syntax checks after fixes
- Maintain good error handling

Now please start handling the simple fix task assigned to you.
"""

    def _post_execute(self, task, response: str) -> str:
        """Process the quick fix result and extract key information."""
        # Extract structured information from the response
        result_info = {
            "fix_applied": self._extract_fix_status(response),
            "files_modified": self._extract_modified_files(response),
            "problem_type": self._extract_problem_type(response),
            "fix_summary": self._extract_fix_summary(response),
            "verification": self._extract_verification(response),
            "full_response": response
        }

        # Add structured info to the response
        structured_section = f"""
=== Fix Execution Report ===
Fix Status: {'✅ Success' if result_info['fix_applied'] else '❌ Incomplete'}
Problem Type: {result_info['problem_type']}
Modified Files: {', '.join(result_info['files_modified']) if result_info['files_modified'] else 'None'}
Fix Summary: {result_info['fix_summary']}
Verification Result: {result_info['verification']}

=== Detailed Execution Process ===
{response}
"""

        return structured_section

    def _extract_fix_status(self, response: str) -> bool:
        """Determine if fix was successfully applied."""
        success_indicators = [
            "fix completed", "successfully fixed", "problem solved", "✅", "fix successful",
            "successfully fixed", "fix applied", "problem solved"
        ]

        failure_indicators = [
            "fix failed", "cannot fix", "error", "❌", "failed",
            "fix failed", "cannot fix", "error", "failed"
        ]

        response_lower = response.lower()

        # Check for explicit failure first
        for indicator in failure_indicators:
            if indicator.lower() in response_lower:
                return False

        # Then check for success
        for indicator in success_indicators:
            if indicator.lower() in response_lower:
                return True

        # Check for tool usage patterns (edit_file, write_file)
        if re.search(r'edit_file|write_file', response):
            return True

        return False

    def _extract_modified_files(self, response: str) -> list:
        """Extract list of files that were modified."""
        files = set()

        # Look for file operation patterns
        file_patterns = [
            r'edit_file.*?["\']([^"\']+)["\']',
            r'write_file.*?["\']([^"\']+)["\']',
            r'modified file[：:]\s*([^\n]+)',
            r'edited[：:]\s*([^\n]+)',
            r'file[：:]\s*([^\n\.]+\.[^\n\s]+)',
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                # Clean up the file path
                file_path = match.strip().replace('`', '')
                if file_path and '.' in file_path:
                    files.add(file_path)

        return list(files)

    def _extract_problem_type(self, response: str) -> str:
        """Extract the type of problem that was fixed."""
        problem_types = {
            "Syntax Error": ["syntax error", "SyntaxError", "syntax error", "missing colon", "missing bracket"],
            "Import Error": ["import error", "ImportError", "ModuleNotFoundError", "import error"],
            "Variable Error": ["NameError", "variable name", "variable error", "name error", "undefined"],
            "Type Error": ["TypeError", "type error", "type error"],
            "Indentation Error": ["IndentationError", "indentation", "indentation"],
            "Other": []
        }

        response_lower = response.lower()

        for problem_type, keywords in problem_types.items():
            for keyword in keywords:
                if keyword.lower() in response_lower:
                    return problem_type

        return "Unknown"

    def _extract_fix_summary(self, response: str) -> str:
        """Extract a concise summary of what was fixed."""
        # Look for summary sections
        summary_patterns = [
            r'fix summary[：:]([^\n]+)',
            r'fix content[：:]([^\n]+)',
            r'solution[：:]([^\n]+)',
            r'Fix summary[：:]([^\n]+)',
        ]

        for pattern in summary_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fallback: try to extract key action sentences
        action_patterns = [
            r'(added [^。\n]+)',
            r'(fixed [^。\n]+)',
            r'(deleted [^。\n]+)',
            r'(corrected [^。\n]+)',
        ]

        for pattern in action_patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1).strip()

        return "Executed code fix operation"

    def _extract_verification(self, response: str) -> str:
        """Extract verification information."""
        verification_patterns = [
            r'verification result[：:]([^\n]+)',
            r'check result[：:]([^\n]+)',
            r'test result[：:]([^\n]+)',
            r'(verification\w*successful)',
            r'(syntax check passed)',
        ]

        for pattern in verification_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Look for bash command execution results
        if "execute_bash_command" in response:
            return "Command verification executed"

        return "No explicit verification"

    def fix_problem_quick(self, problem_description: str) -> Dict[str, Any]:
        """Main method for quick problem fixing.

        Args:
            problem_description: Description of the problem to fix

        Returns:
            Fix result with success status and details
        """
        from core.utils.common import TaskItem, TaskStatus

        task = TaskItem(
            id="quick_fix",
            title="Quick Fix",
            description=f"""
Please quickly diagnose and fix the following problem:

Problem Description: {problem_description}

Please follow the quick fix process:
1. Quickly read relevant files, diagnose specific problems
2. Directly apply the most suitable fix solution
3. Verify the correctness of the fix result

Note: This is a simple fix task, please avoid overly complex analysis and directly perform fix operations.
""",
            agent_type=AgentType.QUICKFIX,
            status=TaskStatus.PENDING,
            dependencies=[]
        )

        result = self.execute(task)

        return {
            "success": result["success"],
            "result": result.get("result", ""),
            "error": result.get("error", None),
            "agent_type": "quickfix",
            "execution_time": "fast"
        }