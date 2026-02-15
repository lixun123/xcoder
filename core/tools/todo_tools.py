


# class TodoManager:
#     """Manages todo files for tracking execution progress."""
#
#     def __init__(self, workspace_dir: str = "workspace"):
#         self.workspace_dir = workspace_dir
#         os.makedirs(self.workspace_dir, exist_ok=True)
#
#     def save_plan(self, plan: FixPlan) -> str:
#         """Save the fix plan to a todo file."""
#         filename = f"fix_plan_{plan.id}.yaml"
#         filepath = os.path.join(self.workspace_dir, filename)
#
#         plan_dict = asdict(plan)
#         # Convert enum values to strings for YAML serialization
#         plan_dict['status'] = plan.status.value
#         for task_dict in plan_dict['tasks']:
#             task_dict['agent_type'] = task_dict['agent_type'].value
#             task_dict['status'] = task_dict['status'].value
#
#         with open(filepath, 'w', encoding='utf-8') as f:
#             yaml.dump(plan_dict, f, default_flow_style=False,
#                      allow_unicode=True, sort_keys=False)
#
#         return filepath
#
#     def load_plan(self, plan_id: str) -> Optional[FixPlan]:
#         """Load a fix plan from todo file."""
#         filename = f"fix_plan_{plan_id}.yaml"
#         filepath = os.path.join(self.workspace_dir, filename)
#
#         if not os.path.exists(filepath):
#             return None
#
#         with open(filepath, 'r', encoding='utf-8') as f:
#             plan_dict = yaml.safe_load(f)
#
#         # Convert string values back to enums
#         plan_dict['status'] = TaskStatus(plan_dict['status'])
#         for task_dict in plan_dict['tasks']:
#             task_dict['agent_type'] = AgentType(task_dict['agent_type'])
#             task_dict['status'] = TaskStatus(task_dict['status'])
#
#         # Reconstruct TaskItem objects
#         tasks = [TaskItem(**task_dict) for task_dict in plan_dict['tasks']]
#         plan_dict['tasks'] = tasks
#
#         return FixPlan(**plan_dict)
#
#     def update_task_status(self, plan_id: str, task_id: str,
#                           status: TaskStatus, result: str = None,
#                           error_message: str = None):
#         """Update task status in the todo file."""
#         plan = self.load_plan(plan_id)
#         if not plan:
#             return False
#
#         for task in plan.tasks:
#             if task.id == task_id:
#                 task.status = status
#                 task.updated_at = datetime.now().isoformat()
#
#                 if status == TaskStatus.IN_PROGRESS:
#                     task.started_at = datetime.now().isoformat()
#                 elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
#                     task.completed_at = datetime.now().isoformat()
#
#                 if result:
#                     task.result = result
#                 if error_message:
#                     task.error_message = error_message
#
#                 break
#
#         plan.updated_at = datetime.now().isoformat()
#         self.save_plan(plan)
#         return True
#
#     def get_next_tasks(self, plan_id: str) -> List[TaskItem]:
#         """Get the next tasks that can be executed (dependencies satisfied)."""
#         plan = self.load_plan(plan_id)
#         if not plan:
#             return []
#
#         completed_task_ids = {
#             task.id for task in plan.tasks
#             if task.status == TaskStatus.COMPLETED
#         }
#
#         next_tasks = []
#         for task in plan.tasks:
#             if task.status == TaskStatus.PENDING:
#                 # Check if all dependencies are completed
#                 if all(dep_id in completed_task_ids for dep_id in task.dependencies):
#                     next_tasks.append(task)
#
#         return next_tasks
