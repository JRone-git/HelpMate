import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..ollama import OllamaClient
from ..executor import ShellExecutor
from ..config import settings

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    task_id: str
    prompt: str
    model: Optional[str] = None
    timeout: Optional[int] = None
    sandbox: bool = False
    elevated: bool = False


@dataclass
class AgentResult:
    """Result from an agent task"""
    task_id: str
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0


class AgentManager:
    """Manages multiple AI agents with orchestration capabilities"""
    
    def __init__(self, ollama_client: OllamaClient, shell_executor: ShellExecutor):
        self.ollama_client = ollama_client
        self.shell_executor = shell_executor
        self.agents: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, AgentResult] = {}
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_agents)
        
    async def create_agent(self, task: AgentTask) -> str:
        """Create and start a new agent"""
        agent_id = f"agent_{len(self.agents) + 1}"
        
        async def agent_worker():
            async with self.semaphore:
                return await self._run_agent(agent_id, task)
        
        task = asyncio.create_task(agent_worker())
        self.agents[agent_id] = task
        
        logger.info(f"Created agent {agent_id} for task {task.task_id}")
        return agent_id
    
    async def _run_agent(self, agent_id: str, task: AgentTask) -> AgentResult:
        """Execute a single agent task"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Agent {agent_id} starting task {task.task_id}")
            
            # Generate response using Ollama
            messages = [{"role": "user", "content": task.prompt}]
            response = await self.ollama_client.chat(messages, task.model)
            
            duration = asyncio.get_event_loop().time() - start_time
            
            result = AgentResult(
                task_id=task.task_id,
                success=True,
                output=response.message.content,
                duration=duration
            )
            
            self.results[task.task_id] = result
            logger.info(f"Agent {agent_id} completed task {task.task_id}")
            
            return result
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            
            result = AgentResult(
                task_id=task.task_id,
                success=False,
                output="",
                error=str(e),
                duration=duration
            )
            
            self.results[task.task_id] = result
            logger.error(f"Agent {agent_id} failed task {task.task_id}: {e}")
            
            return result
    
    async def run_swarm(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """Run multiple agents in parallel (swarm mode)"""
        logger.info(f"Starting swarm with {len(tasks)} agents")
        
        # Create all agents
        agent_ids = []
        for task in tasks:
            agent_id = await self.create_agent(task)
            agent_ids.append(agent_id)
        
        # Wait for all agents to complete
        results = []
        for agent_id in agent_ids:
            try:
                result = await self.agents[agent_id]
                results.append(result)
            except Exception as e:
                logger.error(f"Agent {agent_id} failed: {e}")
        
        logger.info(f"Swarm completed with {len(results)} results")
        return results
    
    async def execute_command(self, command: str, sandbox: bool = False) -> AgentResult:
        """Execute a shell command through an agent"""
        task = AgentTask(
            task_id=f"cmd_{hash(command)}",
            prompt=f"Execute the following command and return the output: {command}",
            sandbox=sandbox
        )
        
        agent_id = await self.create_agent(task)
        result = await self.agents[agent_id]
        
        return result
    
    async def shutdown(self):
        """Shutdown all running agents"""
        logger.info("Shutting down agent manager")
        
        # Cancel all running agents
        for agent_id, task in self.agents.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Agent {agent_id} cancelled")
        
        self.agents.clear()
        self.results.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        return {
            "active_agents": len([t for t in self.agents.values() if not t.done()]),
            "completed_tasks": len([r for r in self.results.values() if r.success]),
            "failed_tasks": len([r for r in self.results.values() if not r.success]),
            "total_agents": len(self.agents)
        }