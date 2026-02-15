#!/usr/bin/env python3
"""
测试脚本用于验证所有工具是否正常工作
"""

from core.agents.entry_agent import execute_bash_command, file_operations, web_search
import os

def test_bash_command():
    """测试bash命令工具"""
    print("=== 测试 bash 命令工具 ===")

    # 测试简单命令
    result1 = execute_bash_command.run("echo 'Hello World'")
    print("测试1 (echo):", result1)

    # 测试列出当前目录
    result2 = execute_bash_command.run("ls -la")
    print("测试2 (ls):", result2)

    # 测试危险命令（应该被阻止）
    result3 = execute_bash_command.run("rm -rf /")
    print("测试3 (危险命令):", result3)

def test_file_operations():
    """测试文件操作工具"""
    print("\n=== 测试文件操作工具 ===")

    # 测试写入文件
    result1 = file_operations.run({"operation": "write", "file_path": "/tmp/test_file.txt", "content": "这是测试内容"})
    print("测试1 (写入):", result1)

    # 测试读取文件
    result2 = file_operations.run({"operation": "read", "file_path": "/tmp/test_file.txt"})
    print("测试2 (读取):", result2)

    # 测试列出目录
    result3 = file_operations.run({"operation": "list", "file_path": "/tmp"})
    print("测试3 (列出):", result3[:200] + "..." if len(result3) > 200 else result3)

def test_web_search():
    """测试网络搜索工具"""
    print("\n=== 测试网络搜索工具 ===")

    # 检查API key是否设置
    if not os.getenv("SERPAPI_API_KEY"):
        print("警告：SERPAPI_API_KEY 未设置，跳过搜索测试")
        return

    # 测试搜索
    result = web_search.run("Python programming language 2024")
    print("搜索结果:", result[:300] + "..." if len(result) > 300 else result)

if __name__ == "__main__":
    print("开始测试所有工具...")

    try:
        # test_bash_command()
        test_file_operations()
        test_web_search()

        print("\n✅ 所有测试完成！")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
