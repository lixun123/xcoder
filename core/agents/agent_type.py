from enum import Enum


class AgentType(Enum):
    """Types of specialized sub_agents."""
    ANALYZER = "analyzer"
    PLANNER = "planner"
    CODER = "coder"
    INTENT = "intent"
    QUICKFIX = "quickfix"
