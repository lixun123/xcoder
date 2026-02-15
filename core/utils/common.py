from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from core.agents.base_sub_agent import AgentType
from typing import List, Dict, Any, Optional

class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskItem:
    """Represents a single task in the execution plan."""
    id: str
    title: str
    description: str
    agent_type: AgentType
    status: TaskStatus
    dependencies: List[str]  # Task IDs this task depends on
    estimated_time: Optional[str] = None
    actual_time: Optional[str] = None
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    context: Optional[Dict[str, Any]] = None  # Additional context information

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class FixPlan:
    """Represents the complete fix plan."""
    id: str
    title: str
    description: str
    problem_analysis: str
    tasks: List[TaskItem]
    created_at: str
    updated_at: str
    status: TaskStatus

    def __post_init__(self):
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if not hasattr(self, 'updated_at') or self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
