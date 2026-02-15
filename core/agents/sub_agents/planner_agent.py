import json
import re
from typing import Dict, Any

from ..base_sub_agent import BaseSubAgent
from ..base_sub_agent import AgentType
from ...utils.common import TaskItem


class PlannerAgent(BaseSubAgent):
    """Specialized agent for task planning and decomposition."""

    def get_agent_type(self) -> AgentType:
        return AgentType.PLANNER

    def get_system_prompt(self) -> str:
        return """
你是一个智能项目规划专家，专门根据代码分析结果制定精准的修复计划。

🎯 规划职责：
1. 深入理解分析结果中发现的具体问题
2. 将修复任务分解为可执行的步骤
3. 根据问题类型选择最适合的专业agent
4. 设置合理的任务依赖关系和执行顺序
5. 估算每个任务的复杂度和时间

📋 输出格式（必须返回有效JSON）：
{
  "plan_summary": "计划总体概述",
  "complexity_assessment": "simple|medium|complex",
  "estimated_total_time": "预估总时间",
  "risk_factors": ["潜在风险因素"],
  "tasks": [
    {
      "id": "task_1",
      "title": "具体任务标题",
      "description": "详细任务描述（包括具体要修复的问题和文件）",
      "agent_type": "coder",
      "dependencies": [],
      "estimated_time": "10-30分钟|30-90分钟|2-8小时",
      "priority": "high|medium|low"
    }
  ]
}

**重要：必须返回有效的JSON格式，不要添加额外的文字说明。**
        """

    def _post_execute(self, task: TaskItem, response: str) -> str:
        """Post-process planning results to ensure valid JSON."""
        # Try to extract and validate JSON from response
        plan_json = self._extract_and_validate_json(response)
        return json.dumps(plan_json, ensure_ascii=False, indent=2)

    def _extract_and_validate_json(self, response: str) -> Dict[str, Any]:
        """Extract and validate JSON from planner response."""
        json_patterns = [
            r'\{.*\}',
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    json_str = match if isinstance(match, str) else response
                    plan_data = json.loads(json_str)

                    # Validate required fields
                    if "tasks" in plan_data and isinstance(plan_data["tasks"], list):
                        return plan_data
                except json.JSONDecodeError:
                    continue

        return None
