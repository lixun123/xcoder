"""
Simple file editing tools for CodeFixAgent
"""

from langchain.tools import tool
from core.utils.confirmation import request_user_confirmation, is_sensitive_file


@tool
def edit_file(file_path: str, old_text: str, new_text: str) -> str:
    """Edit a file by replacing old text with new text.

    Args:
        file_path: Path to the file to edit
        old_text: Text to find and replace
        new_text: Text to replace with

    Returns:
        Result message indicating success or failure
    """
    # 检查是否为敏感文件，需要用户确认
    if is_sensitive_file(file_path):
        if not request_user_confirmation(
            action="文件修改",
            details=f"修改敏感文件内容",
            file_path=file_path
        ):
            return "❌ 用户取消了文件修改操作"

    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if old_text exists
        if old_text not in content:
            return f"❌ 在文件 {file_path} 中未找到要替换的文本: '{old_text}'"

        # Replace the text
        new_content = content.replace(old_text, new_text)

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"✅ 成功修改文件 {file_path}\n原文本: {old_text}\n新文本: {new_text}"

    except FileNotFoundError:
        return f"❌ 文件 {file_path} 不存在"
    except Exception as e:
        return f"❌ 编辑文件时出错: {str(e)}"


@tool
def read_file_with_lines(file_path: str) -> str:
    """Read a file and return content with line numbers for easy editing.

    Args:
        file_path: Path to the file to read

    Returns:
        File content with line numbers
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return f"文件 {file_path} 是空的"

        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i:3d}: {line.rstrip()}")

        return f"文件 {file_path} (共{len(lines)}行):\n" + "\n".join(numbered_lines)

    except FileNotFoundError:
        return f"❌ 文件 {file_path} 不存在"
    except Exception as e:
        return f"❌ 读取文件时出错: {str(e)}"