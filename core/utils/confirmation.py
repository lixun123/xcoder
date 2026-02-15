#!/usr/bin/env python3
"""
人工确认工具
"""

import sys
from typing import Optional


def request_user_confirmation(
    action: str,
    details: str,
    file_path: Optional[str] = None,
    command: Optional[str] = None
) -> bool:
    """
    请求用户确认危险操作

    Args:
        action: 操作类型 ('文件写入', '文件修改', 'bash命令')
        details: 操作详情
        file_path: 文件路径（如果适用）
        command: 命令内容（如果适用）

    Returns:
        bool: 用户是否确认
    """
    print("🚨 需要用户确认")
    print("=" * 50)
    print(f"操作类型: {action}")
    print(f"详情: {details}")

    if file_path:
        print(f"文件路径: {file_path}")

    if command:
        print(f"命令: {command}")

    print("=" * 50)

    while True:
        try:
            user_input = input("是否继续执行? (y/yes/n/no): ").strip().lower()

            if user_input in ['y', 'yes', '是', 'y是']:
                print("✅ 用户确认，继续执行...")
                return True
            elif user_input in ['n', 'no', '否', 'n否']:
                print("❌ 用户取消操作")
                return False
            else:
                print("请输入 y/yes 或 n/no")

        except KeyboardInterrupt:
            print("\n❌ 用户取消操作")
            return False
        except EOFError:
            print("\n❌ 输入流结束，默认取消操作")
            return False


def is_sensitive_file(file_path: str) -> bool:
    """
    判断是否为敏感文件
    """
    sensitive_patterns = [
        '/.env', '/config', '/setting', '/passwd', '/shadow',
        '/ssh/', '/.ssh/', '/private', '/secret', '/key',
        '/etc/', '/boot/', '/sys/', '/proc/', '/dev/',
        '.key', '.pem', '.crt', '.p12', '.pfx'
    ]

    file_path_lower = file_path.lower()
    return any(pattern in file_path_lower for pattern in sensitive_patterns)


def is_dangerous_command(command: str) -> bool:
    """
    判断是否为危险命令
    """
    dangerous_patterns = [
        'rm', 'del', 'delete', 'format', 'mkfs', 'fdisk',
        'shutdown', 'reboot', 'halt', 'poweroff',
        'chmod', 'chown', 'passwd', 'su ', 'sudo',
        'kill', 'killall', 'pkill',
        '>', '>>', 'dd', 'mv', 'cp',
        'curl', 'wget', 'git clone',
        'pip install', 'npm install', 'apt install'
    ]

    command_lower = command.lower().strip()
    return any(pattern in command_lower for pattern in dangerous_patterns)