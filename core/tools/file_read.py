"""
Read-only file operations tools for agents with restricted permissions
"""

import os
from langchain.tools import tool
from .file_path_utils import resolve_file_path, find_project_files


@tool
def read_file(file_path: str, base_dir: str = None) -> str:
    """Read file content with intelligent path resolution.

    Args:
        file_path: Path to the file (supports relative paths and smart resolution)
        base_dir: Base directory for path resolution (optional)

    Returns:
        File content or error message
    """
    try:
        # Resolve the file path intelligently
        resolved_path = resolve_file_path(file_path, base_dir)

        if not os.path.exists(resolved_path):
            # Try to suggest similar files
            suggestions = find_project_files(os.path.basename(file_path))
            if suggestions:
                suggestion_text = "\n建议的类似文件:\n" + "\n".join(suggestions[:5])
                return f"文件未找到: {resolved_path}{suggestion_text}"
            else:
                return f"文件未找到: {resolved_path}"

        with open(resolved_path, 'r', encoding='utf-8') as f:
            content_text = f.read()
        return f"文件内容 ({resolved_path}):\n{content_text}"

    except Exception as e:
        return f"文件读取错误: {str(e)}"


@tool
def list_files(directory_path: str, base_dir: str = None) -> str:
    """List directory contents with intelligent path resolution.

    Args:
        directory_path: Path to the directory (supports relative paths and smart resolution)
        base_dir: Base directory for path resolution (optional)

    Returns:
        Directory listing or error message
    """
    try:
        # Resolve the directory path intelligently
        resolved_path = resolve_file_path(directory_path, base_dir)

        if os.path.isdir(resolved_path):
            files = os.listdir(resolved_path)
            # Sort files and directories separately
            dirs = [f for f in files if os.path.isdir(os.path.join(resolved_path, f))]
            files_only = [f for f in files if os.path.isfile(os.path.join(resolved_path, f))]

            result = f"目录 {resolved_path} 内容:\n"
            if dirs:
                result += "📁 目录: " + ", ".join(sorted(dirs)) + "\n"
            if files_only:
                result += "📄 文件: " + ", ".join(sorted(files_only))
            return result
        else:
            return f"{resolved_path} 不是有效目录"

    except Exception as e:
        return f"目录列表错误: {str(e)}"


@tool
def find_files(pattern: str, base_dir: str = None) -> str:
    """Find files matching a pattern in the project directory.

    Args:
        pattern: File pattern to search for (supports wildcards)
        base_dir: Base directory to search from

    Returns:
        List of matching files or error message
    """
    try:
        matches = find_project_files(pattern, base_dir)
        if matches:
            return f"Found {len(matches)} matching files:\n" + "\n".join(matches)
        else:
            return f"No files found matching pattern: {pattern}"

    except Exception as e:
        return f"文件查找错误: {str(e)}"
