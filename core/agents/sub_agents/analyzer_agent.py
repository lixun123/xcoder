import json
from typing import Dict, Any

from core.llm import get_llm_provider
from core.agents.base_sub_agent import BaseSubAgent
from core.tools.tool_manager import AgentType, tool_manager
from core.utils.common import TaskItem


class AnalyzerAgent(BaseSubAgent):
    """Specialized agent for code analysis and problem identification."""

    def get_agent_type(self) -> AgentType:
        return AgentType.ANALYZER

    def get_system_prompt(self) -> str:
        return """
你是一个专业的代码分析专家。当接到分析任务时，你需要：

🔍 主动分析能力：
1. 使用file_operations工具读取和检查相关文件
2. 识别代码中的语法错误、导入问题、类型问题等
3. 分析代码结构和依赖关系
4. 检查是否有运行时错误的潜在原因
5. 使用web_search查找相关错误的解决方案

📊 分析输出格式：
请以结构化方式提供分析结果：

**文件状态：**
- 文件是否存在和可读
- 基本代码结构

**发现的问题：**
- 语法错误（具体行号和错误类型）
- 导入问题（缺失的包或模块）
- 类型检查警告
- 逻辑错误和潜在bug

**影响评估：**
- 问题的严重程度
- 影响范围
- 是否阻塞程序运行

**建议解决方案：**
- 针对每个问题的修复建议
- 修复的优先级顺序

请主动使用工具分析文件，提供详细的技术分析报告。
        """

    def _post_execute(self, task: TaskItem, response: str) -> str:
        """Post-process analysis results."""
        # Extract structured information from response
        return response

    def _extract_analysis_data(self, response: str) -> Dict[str, Any]:
        """Extract structured data from analysis response."""
        # Simple extraction logic - could be enhanced with better parsing
        analysis_data = {
            "problems_found": [],
            "severity": "unknown",
            "files_analyzed": []
        }

        # Look for problem indicators
        if "错误" in response or "问题" in response:
            analysis_data["problems_found"].append("发现问题")

        if "严重" in response or "critical" in response.lower():
            analysis_data["severity"] = "high"
        elif "轻微" in response or "minor" in response.lower():
            analysis_data["severity"] = "low"
        else:
            analysis_data["severity"] = "medium"

        return analysis_data

if __name__ == "__main__":
    # Test code removed for production build
    pass
