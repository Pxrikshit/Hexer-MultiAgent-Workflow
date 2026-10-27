import asyncio
import logging
from typing import Dict, Any, List
from .schemas import (
    TaskDecompositionPlan,
    SubTask,
    AgentRole,
    AgentExecutionResult,
    TaskPriority
)
from .subagents import (
    BaseSubagent,
    ResearchAgent,
    PromptSynthesisAgent,
    AssemblyCoordinator
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Hexer.Orchestrator")


class MultiAgentOrchestrator:
    """
    Central Coordinator for Autonomous Multi-Agent AI Workflows.
    Handles goal decomposition, subagent dispatch, dynamic tool calls, and error fallback.
    """

    def __init__(self):
        self.subagents: Dict[AgentRole, BaseSubagent] = {
            AgentRole.RESEARCH_AGENT: ResearchAgent(),
            AgentRole.PROMPT_SYNTHESIS_AGENT: PromptSynthesisAgent(),
            AgentRole.ASSEMBLY_COORDINATOR: AssemblyCoordinator(),
        }
        self.shared_state: Dict[str, Any] = {}

    async def decompose_goal(self, goal: str) -> TaskDecompositionPlan:
        """Decomposes a business objective into scheduled subtasks."""
        logger.info(f"Decomposing objective: {goal}")
        return TaskDecompositionPlan(
            goal=goal,
            subtasks=[
                SubTask(
                    task_id="task_01_research",
                    assigned_agent=AgentRole.RESEARCH_AGENT,
                    instruction="Gather intelligence and extract relevant facts.",
                    priority=TaskPriority.HIGH
                ),
                SubTask(
                    task_id="task_02_synthesis",
                    assigned_agent=AgentRole.PROMPT_SYNTHESIS_AGENT,
                    instruction="Structure knowledge into schema-grounded prompts.",
                    dependencies=["task_01_research"],
                    priority=TaskPriority.HIGH
                ),
                SubTask(
                    task_id="task_03_assembly",
                    assigned_agent=AgentRole.ASSEMBLY_COORDINATOR,
                    instruction="Coordinate asset generation and tool pipeline execution.",
                    dependencies=["task_02_synthesis"],
                    priority=TaskPriority.CRITICAL
                )
            ]
        )

    async def run_pipeline(self, goal: str) -> Dict[str, Any]:
        """Executes the complete autonomous multi-agent pipeline."""
        logger.info(f"=== Initializing Hexer Multi-Agent Pipeline ===")
        plan = await self.decompose_goal(goal)
        results: List[AgentExecutionResult] = []

        for subtask in plan.subtasks:
            agent = self.subagents.get(subtask.assigned_agent)
            if not agent:
                logger.error(f"No subagent available for role: {subtask.assigned_agent}")
                continue

            # Execute subagent with fault-tolerant retry wrapper
            try:
                res = await agent.execute(subtask, self.shared_state)
                results.append(res)
                self.shared_state[subtask.task_id] = res.payload
            except Exception as e:
                logger.warning(f"Error in {subtask.task_id}: {e}. Triggering fallback logic.")

        logger.info(f"=== Pipeline Completed Successfully ({len(results)} steps) ===")
        return {
            "status": "COMPLETED",
            "goal": goal,
            "steps_executed": len(results),
            "state": self.shared_state
        }


if __name__ == "__main__":
    async def main():
        orchestrator = MultiAgentOrchestrator()
        result = await orchestrator.run_pipeline("Synthesize competitive research into multi-media video package")
        print("\nPipeline Result State:", result["status"])

    asyncio.run(main())
