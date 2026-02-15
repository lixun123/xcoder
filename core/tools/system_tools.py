"""
System operation tools for LangChain Agent
"""

import subprocess
from langchain.tools import tool
from core.utils.confirmation import request_user_confirmation, is_dangerous_command


@tool
def execute_bash_command(command: str) -> str:
    """Execute bash commands safely.

    Args:
        command: Bash command to execute

    Returns:
        Command output or error message

    注意：为了安全考虑，某些危险命令会被阻止执行
    """
    # 定义危险命令列表（为了安全）
    dangerous_commands = [
        'rm -rf /',
        'format',
        'del /s',
        'shutdown',
        'reboot',
        'halt',
        'poweroff',
        'dd if=',
        'mkfs',
        'fdisk',
        'passwd',
        'sudo su',
        'chmod 777',
        '> /dev/',
        'mv * /',
        'cp * /',
        'chown',
        'killall',
        'kill -9'
    ]

    # 检查命令是否包含危险操作
    command_lower = command.lower()
    for dangerous_cmd in dangerous_commands:
        if dangerous_cmd in command_lower:
            return f"危险命令被阻止执行: {command}\n原因: 包含潜在危险操作 '{dangerous_cmd}'"

    # 检查是否为危险命令，需要用户确认
    if is_dangerous_command(command):
        if not request_user_confirmation(
            action="bash命令",
            details="执行可能危险的命令",
            command=command
        ):
            return "❌ 用户取消了命令执行"

    try:
        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )

        # 构造返回结果
        output = f"命令: {command}\n"
        output += f"返回码: {result.returncode}\n"

        if result.stdout:
            output += f"标准输出:\n{result.stdout}\n"

        if result.stderr:
            output += f"标准错误:\n{result.stderr}\n"

        if result.returncode != 0:
            output += f"命令执行失败，返回码: {result.returncode}"

        return output

    except subprocess.TimeoutExpired:
        return f"命令执行超时 (30秒): {command}"
    except Exception as e:
        return f"执行命令时发生错误: {str(e)}"