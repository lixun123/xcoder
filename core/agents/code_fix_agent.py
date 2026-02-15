#!/usr/bin/env python3
"""
CodeFixAgent - Advanced Fix Agent with Planning and Subagent Management

This module creates an advanced agent that can handle complex fix tasks by:
1. Analyzing problems and creating detailed plans
2. Managing todo files to track execution steps
3. Calling specialized sub_agents for different phases
4. Providing error recovery and retry mechanisms
"""

import os
import json
import uuid
from dataclasses import asdict

import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional


from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver, logger

from core.llm import get_llm_provider
from core.agents.sub_agents.analyzer_agent import AnalyzerAgent
from core.agents.sub_agents.coder_agent import CoderAgent
from core.agents.sub_agents.planner_agent import PlannerAgent
from core.agents.intent_agent import IntentAgent
from core.agents.quick_fix_agent import QuickFixAgent
# from core.tools.todo_tools import TodoManager
from core.tools.tool_manager import tool_manager, AgentType
from core.utils.common import TaskItem, TaskStatus, FixPlan
from core.agents.base_sub_agent import BaseSubAgent



class TodoManager:
    """Manages todo files for tracking execution progress."""

    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = workspace_dir
        os.makedirs(self.workspace_dir, exist_ok=True)

    def save_plan(self, plan: FixPlan) -> str:
        """Save the fix plan to a todo file."""
        filename = f"fix_plan_{plan.id}.yaml"
        filepath = os.path.join(self.workspace_dir, filename)

        plan_dict = asdict(plan)
        # Convert enum values to strings for YAML serialization
        plan_dict['status'] = plan.status.value
        for task_dict in plan_dict['tasks']:
            task_dict['agent_type'] = task_dict['agent_type'].value
            task_dict['status'] = task_dict['status'].value

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(plan_dict, f, default_flow_style=False,
                     allow_unicode=True, sort_keys=False)

        return filepath

    def load_plan(self, plan_id: str) -> Optional[FixPlan]:
        """Load a fix plan from todo file."""
        filename = f"fix_plan_{plan_id}.yaml"
        filepath = os.path.join(self.workspace_dir, filename)

        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            plan_dict = yaml.safe_load(f)

        # Convert string values back to enums
        plan_dict['status'] = TaskStatus(plan_dict['status'])
        for task_dict in plan_dict['tasks']:
            task_dict['agent_type'] = AgentType(task_dict['agent_type'])
            task_dict['status'] = TaskStatus(task_dict['status'])

        # Reconstruct TaskItem objects
        tasks = [TaskItem(**task_dict) for task_dict in plan_dict['tasks']]
        plan_dict['tasks'] = tasks

        return FixPlan(**plan_dict)

    def update_task_status(self, plan_id: str, task_id: str,
                          status: TaskStatus, result: str = None,
                          error_message: str = None):
        """Update task status in the todo file."""
        plan = self.load_plan(plan_id)
        if not plan:
            return False

        for task in plan.tasks:
            if task.id == task_id:
                task.status = status
                task.updated_at = datetime.now().isoformat()

                if status == TaskStatus.IN_PROGRESS:
                    task.started_at = datetime.now().isoformat()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.now().isoformat()

                if result:
                    task.result = result
                if error_message:
                    task.error_message = error_message

                break

        plan.updated_at = datetime.now().isoformat()
        self.save_plan(plan)
        return True

    def get_next_tasks(self, plan_id: str) -> List[TaskItem]:
        """Get the next tasks that can be executed (dependencies satisfied)."""
        plan = self.load_plan(plan_id)
        if not plan:
            return []

        completed_task_ids = {
            task.id for task in plan.tasks
            if task.status == TaskStatus.COMPLETED
        }

        next_tasks = []
        for task in plan.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                if all(dep_id in completed_task_ids for dep_id in task.dependencies):
                    next_tasks.append(task)

        return next_tasks


class CodeFixAgent:
    """Advanced agent for handling complex code fix tasks."""

    def __init__(self, provider: str = None, model: str = None,
                 base_url: str = None, api_key: str = None):
        """Initialize CodeFixAgent.

        Args:
            provider: LLM provider type ('ollama' or 'zhipuai')
            model: Model name
            base_url: Provider base URL (for Ollama)
            api_key: API key (for cloud providers)
        """
        self.provider_type = provider or os.getenv("LLM_PROVIDER", "ollama")
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.llm = self._create_llm()
        self.tools = tool_manager.get_basic_tools()
        self.todo_manager = TodoManager()
        self.subagents = self._create_subagents()

        # Main planning agent
        self.main_prompt = """
你是一个高级的代码问题修复专家，专门处理复杂的软件修复任务。
你的能力包括：
1. 深度分析代码问题并制定详细的修复计划
2. 将复杂任务分解为可管理的步骤
3. 协调各种专业子代理来完成不同阶段的工作
4. 监控执行进度并处理异常情况

请始终以系统化、专业化的方式处理代码修复任务。
        """
        self.main_agent = self._create_main_agent()

    def _create_llm(self):
        """Create LLM instance based on configured provider."""
        provider_config = {
            "model": self.model,
            "base_url": self.base_url,
        }

        if self.api_key:
            provider_config["api_key"] = self.api_key

        client = get_llm_provider(self.provider_type, **provider_config)
        return client.generate_llm()

    def _create_subagents(self) -> Dict[AgentType, BaseSubAgent]:
        """Create specialized sub_agents with appropriate tools."""
        subagents = {}
        # Map of agent types to their implementation classes
        agent_map = {
            AgentType.ANALYZER: AnalyzerAgent,
            AgentType.PLANNER: PlannerAgent,
            AgentType.CODER: CoderAgent,
            AgentType.INTENT: IntentAgent,
            AgentType.QUICKFIX: QuickFixAgent
        }
        for agent_type in AgentType:
            # Get specialized tools for this agent type
            specialized_tools = tool_manager.get_tools_for_agent(agent_type)
            agent_class = agent_map.get(agent_type)
            if agent_class:
                subagents[agent_type] = agent_class(self.llm, specialized_tools)
                # Agent configured successfully
        return subagents

    def _create_main_agent(self):
        """Create the main planning agent."""
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.main_prompt,
            checkpointer=InMemorySaver()
        )

    def classify_problem_intent(self, problem_description: str) -> Dict[str, Any]:
        """Classify problem complexity to determine handling path."""
        logger.info("🎯 开始问题复杂度分类...")

        intent_agent = self.subagents[AgentType.INTENT]
        classification = intent_agent.classify_problem(problem_description)

        print(f"📊 问题分类结果:")
        print(f"   - 复杂度: {classification['intent']}")
        print(f"   - 置信度: {classification['confidence']:.2f}")
        print(f"   - 理由: {classification['reasoning']}")

        return classification

    def fix_problem_simple(self, problem_description: str) -> Dict[str, Any]:
        """Handle simple problems using QuickFixAgent."""
        logger.info("⚡ 使用简单修复路径...")

        quickfix_agent = self.subagents[AgentType.QUICKFIX]
        result = quickfix_agent.fix_problem_quick(problem_description)

        if result["success"]:
            print("✅ 简单修复完成")
        else:
            print(f"❌ 简单修复失败: {result.get('error', 'unknown')}")

        return result

    def analyze_problem(self, problem_description: str) -> Dict[str, Any]:
        """Analyze the problem and create initial assessment."""
        analyzer = self.subagents[AgentType.ANALYZER]

        task = TaskItem(
            id="analysis",
            title="问题分析",
            description=f"分析以下问题: {problem_description}",
            agent_type=AgentType.ANALYZER,
            status=TaskStatus.PENDING,
            dependencies=[]
        )

        result = analyzer.execute(task)
        return result

    def create_fix_plan(self, problem_description: str,
                       analysis_result: Dict[str, Any]) -> FixPlan:
        """Create a comprehensive fix plan using intelligent planner agent."""
        logger.info("🤖 调用智能规划agent制定修复计划...")

        planner = self.subagents[AgentType.PLANNER]

        # Build detailed planning context
        planning_prompt = f"""
请基于以下信息制定详细的代码修复计划：

🔍 原始问题：
{problem_description}

📊 问题分析结果：
{analysis_result.get("result", "")}

请分析问题的复杂度，合理分解任务，并制定最优的执行计划。
重点考虑：
1. 问题的根本原因和影响范围
2. 修复步骤的逻辑顺序
3. 每个步骤需要的专业技能（选择合适的agent类型）
4. 任务间的依赖关系
5. 潜在的风险点

返回格式化的JSON计划。
        """

        task = TaskItem(
            id="planning",
            title="制定修复计划",
            description=planning_prompt,
            agent_type=AgentType.PLANNER,
            status=TaskStatus.PENDING, # todo 这个是干嘛的
            dependencies=[]
        )

        result = planner.execute(task) # todo planner这里不需要few shot吗？这一步为什么这么慢

        if not result["success"]:
            print(f"❌ 规划失败: {result['error']}")
            raise
            # Fallback to default plan # todo 兜底
            # return self._create_fallback_plan(problem_description, analysis_result)

        # Parse the planner's response to extract JSON plan
        plan_content = result["result"]

        try:
            # Try to extract JSON from the response
            plan_data = self._parse_plan_from_response(plan_content) # todo 两步多余了

            if plan_data:
                tasks = self._convert_plan_to_tasks(plan_data)

                plan = FixPlan(
                    id=str(uuid.uuid4()),
                    title=f"修复计划: {problem_description[:50]}...",
                    description=problem_description,
                    problem_analysis=analysis_result.get("result", ""),
                    tasks=tasks,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    status=TaskStatus.PENDING
                )

                print(f"✅ 成功生成包含 {len(tasks)} 个任务的修复计划")
                return plan
            else:
                print("⚠️ 无法解析规划结果，使用备用计划")
                return None

        except Exception as e:
            print(f"❌ 解析规划结果时出错: {str(e)}")
            # return self._create_fallback_plan(problem_description, analysis_result)
            return None


    def _parse_plan_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON plan from planner agent response."""
        import re

        # Try to find JSON content in the response
        json_patterns = [
            r'\{.*\}',  # Simple brace matching
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*?\})\s*```',  # Generic code blocks
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    # If pattern captured groups, use the first group
                    json_str = match if isinstance(match, str) else match[0] if match else response
                    plan_data = json.loads(json_str)

                    # Validate required fields
                    if "tasks" in plan_data and isinstance(plan_data["tasks"], list):
                        return plan_data

                except json.JSONDecodeError:
                    continue

        # If no JSON found, try to parse the entire response
        try:
            plan_data = json.loads(response.strip())
            if "tasks" in plan_data:
                return plan_data
        except json.JSONDecodeError:
            pass

        print("⚠️ 无法从响应中提取有效的JSON计划")
        return None

    def _convert_plan_to_tasks(self, plan_data: Dict[str, Any]) -> List[TaskItem]:
        """Convert parsed plan data to TaskItem objects."""
        tasks = []

        for task_data in plan_data.get("tasks", []):
            try:
                # Map agent type string to enum
                agent_type_str = task_data.get("agent_type", "coder")
                agent_type = AgentType(agent_type_str.lower())

                task = TaskItem(
                    id=task_data.get("id", f"task_{len(tasks) + 1}"),
                    title=task_data.get("title", "未命名任务"),
                    description=task_data.get("description", ""),
                    agent_type=agent_type,
                    status=TaskStatus.PENDING,
                    dependencies=task_data.get("dependencies", []),
                    estimated_time=task_data.get("estimated_time", "未知"),
                )

                tasks.append(task)
                print(f"📝 创建任务: {task.title} ({task.agent_type.value})")

            except (ValueError, KeyError) as e:
                print(f"⚠️ 跳过无效任务: {e}")
                continue

        return tasks

    def execute_plan(self, plan: FixPlan) -> Dict[str, Any]:
        """Execute the fix plan step by step."""
        print(f"开始执行修复计划: {plan.title}")
        print(f"任务总数: {len(plan.tasks)}")
        print("-" * 50)

        # Save the plan
        plan_file = self.todo_manager.save_plan(plan)
        print(f"计划已保存到: {plan_file}")

        execution_log = []

        while True:
            # Get next tasks that can be executed
            next_tasks = self.todo_manager.get_next_tasks(plan.id)

            if not next_tasks:
                # Reload plan from file to get latest task statuses
                updated_plan = self.todo_manager.load_plan(plan.id)
                if not updated_plan:
                    print("❌ 无法加载计划文件")
                    break

                # Check if all tasks are completed using updated plan
                remaining_tasks = [
                    task for task in updated_plan.tasks
                    if task.status not in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]
                ]

                if not remaining_tasks:
                    logger.info("\n✅ 所有任务已完成!")
                    break
                else:
                    print(f"\n❌ 还有 {len(remaining_tasks)} 个任务待完成，但无法继续执行")
                    print("可能存在依赖问题或任务失败")
                    break

            # Execute next tasks
            for task in next_tasks:
                print(f"\n🔄 执行任务: {task.title}")
                print(f"   类型: {task.agent_type.value}")
                print(f"   描述: {task.description}")

                # Update task status to in_progress
                self.todo_manager.update_task_status(
                    plan.id, task.id, TaskStatus.IN_PROGRESS
                )

                # Execute the task
                try:
                    subagent = self.subagents[task.agent_type]
                    result = subagent.execute(task)

                    if result["success"]:
                        print(f"   ✅ 任务完成")
                        self.todo_manager.update_task_status(
                            plan.id, task.id, TaskStatus.COMPLETED,
                            result=result["result"]
                        )
                        execution_log.append({
                            "task_id": task.id,
                            "status": "completed",
                            "result": result["result"]
                        })
                    else:
                        print(f"   ❌ 任务失败: {result['error']}")

                        # Handle retry logic # todo 有bug
                        if task.retry_count < task.max_retries:
                            task.retry_count += 1
                            print(f"   🔄 重试 ({task.retry_count}/{task.max_retries})")
                            self.todo_manager.update_task_status(
                                plan.id, task.id, TaskStatus.PENDING,
                                error_message=result["error"]
                            )
                        else:
                            print(f"   ❌ 任务最终失败，已达到最大重试次数")
                            self.todo_manager.update_task_status(
                                plan.id, task.id, TaskStatus.FAILED,
                                error_message=result["error"]
                            )

                        execution_log.append({
                            "task_id": task.id,
                            "status": "failed",
                            "error": result["error"],
                            "retry_count": task.retry_count
                        })

                except Exception as e:
                    print(f"   💥 执行异常: {str(e)}")
                    self.todo_manager.update_task_status(
                        plan.id, task.id, TaskStatus.FAILED,
                        error_message=str(e)
                    )

        return {
            "plan_id": plan.id,
            "plan_file": plan_file,
            "execution_log": execution_log
        }

    def fix_problem(self, problem_description: str) -> Dict[str, Any]:
        """Main method to fix a problem end-to-end with dual-path routing."""
        print(f"🚀 开始处理问题: {problem_description}")
        print("=" * 60)

        # Step 1: Intent Classification
        print("\n🎯 步骤 1: 问题复杂度分类...")
        classification = self.classify_problem_intent(problem_description)

        # Determine routing path based on classification
        intent = classification.get("intent", "complex")
        confidence = classification.get("confidence", 0.0)

        # Use confidence threshold for routing decisions
        confidence_threshold = 0.7

        if intent == "simple" and confidence >= confidence_threshold:
            print(f"\n⚡ 选择简单修复路径 (置信度: {confidence:.2f})")
            print("-" * 40)

            # Simple path: Direct fix using QuickFixAgent
            simple_result = self.fix_problem_simple(problem_description)

            if simple_result["success"]:
                print("\n✅ 简单修复路径执行成功")
                return {
                    "success": True,
                    "path": "simple",
                    "classification": classification,
                    "result": simple_result,
                    "execution_time": "快速"
                }
            else:
                print("\n⚠️ 简单修复失败，降级到复杂流程...")
                # Fallback to complex path
                return self._execute_complex_path(problem_description, classification, simple_result)

        else:
            print(f"\n🔄 选择复杂修复路径 (intent: {intent}, 置信度: {confidence:.2f})")
            print("-" * 40)

            # Complex path: Traditional three-step process
            return self._execute_complex_path(problem_description, classification)

    def _execute_complex_path(self, problem_description: str, classification: Dict[str, Any],
                             failed_simple_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the traditional complex fix path."""
        fallback_context = ""
        if failed_simple_result:
            fallback_context = f"\n(注意：简单修复尝试失败，错误: {failed_simple_result.get('error', 'unknown')})"

        # Step 2: Detailed Analysis
        print("\n📊 步骤 2: 详细问题分析...")
        analysis_result = self.analyze_problem(problem_description + fallback_context)

        if not analysis_result["success"]:
            return {
                "success": False,
                "error": "问题分析失败",
                "path": "complex",
                "classification": classification,
                "failed_simple_result": failed_simple_result,
                "details": analysis_result
            }

        print("✅ 问题分析完成")

        # Step 3: Create fix plan
        print("\n📋 步骤 3: 制定修复计划...")
        fix_plan = self.create_fix_plan(problem_description, analysis_result)

        if not fix_plan:
            return {
                "success": False,
                "error": "修复计划创建失败",
                "path": "complex",
                "classification": classification,
                "analysis": analysis_result,
                "failed_simple_result": failed_simple_result
            }

        print("✅ 修复计划创建完成")
        for task in fix_plan.tasks:
            print(f"{task.title}: {task.description}")

        # Step 4: Execute the plan
        print("\n⚡ 步骤 4: 执行修复计划...")
        execution_result = self.execute_plan(fix_plan)

        return {
            "success": True,
            "path": "complex",
            "classification": classification,
            "analysis": analysis_result,
            "plan": fix_plan,
            "execution": execution_result,
            "failed_simple_result": failed_simple_result
        }


def main():
    """Main function for testing."""
    # Test code removed for production build
    pass


if __name__ == "__main__":
    # 可以直接运行进入交互模式，也可以调用main()测试
    main()
