"""
Write operations tools for agents with full file permissions
"""

import os
from langchain.tools import tool
from .file_path_utils import resolve_file_path
from core.utils.confirmation import request_user_confirmation, is_sensitive_file


@tool
def write_file(file_path: str, content: str, base_dir: str = None) -> str:
    """Write content to file with intelligent path resolution and user confirmation.

    Args:
        file_path: Path to the file (supports relative paths and smart resolution)
        content: Content to write to the file
        base_dir: Base directory for path resolution (optional)

    Returns:
        Success message or error message
    """
    try:
        # Resolve the file path intelligently
        resolved_path = resolve_file_path(file_path, base_dir)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)

        # Check if file exists and request confirmation for overwrite
        if os.path.exists(resolved_path):
            if not request_user_confirmation(
                action="文件覆盖",
                details=f"文件已存在，将被覆盖",
                file_path=resolved_path
            ):
                return "❌ 用户取消了文件覆盖操作"

        # Check if sensitive file and request confirmation
        elif is_sensitive_file(resolved_path):
            if not request_user_confirmation(
                action="文件写入",
                details=f"写入敏感文件",
                file_path=resolved_path
            ):
                return "❌ 用户取消了文件写入操作"

        # Write the file
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"文件 {resolved_path} 写入成功"

    except Exception as e:
        return f"文件写入错误: {str(e)}"
