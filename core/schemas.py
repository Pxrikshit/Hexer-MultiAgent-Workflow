from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AgentRole(str, Enum):
    ORCHESTRATOR = "ORCHESTRATOR"
    RESEARCH_AGENT = "RESEARCH_AGENT"
    PROMPT_SYNTHESIS_AGENT = "PROMPT_SYNTHESIS_AGENT"
    ASSEMBLY_COORDINATOR = "ASSEMBLY_COORDINATOR"


class SubTask(BaseModel):
    task_id: str = Field(description="Unique identifier for the subtask")
    assigned_agent: AgentRole = Field(description="Subagent responsible for execution")
    instruction: str = Field(description="Concrete actionable instruction")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    dependencies: List[str] = Field(default_factory=list)
    output_schema: Optional[Dict[str, Any]] = Field(default=None)


class TaskDecompositionPlan(BaseModel):
    goal: str = Field(description="High-level business goal")
    subtasks: List[SubTask] = Field(description="Ordered list of decoupled subtasks")
    estimated_duration_seconds: float = Field(default=0.0)


class ToolInvocation(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    caller_agent: str
    timeout_seconds: int = 30


class AgentExecutionResult(BaseModel):
    task_id: str
    agent_role: AgentRole
    status: str = Field(description="SUCCESS, FAILED, or RETRIED")
    payload: Dict[str, Any] = Field(default_factory=dict)
    execution_time_seconds: float
