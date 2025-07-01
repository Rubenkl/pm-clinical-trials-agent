"""Base agent classes and response models."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Standard response model for all agents."""
    
    success: bool
    content: str
    agent_id: str
    execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseAgent:
    """Base class for all clinical trial agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._performance_metrics = {
            "requests_processed": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_execution_time": 0.0
        }
    
    async def process_message(self, message: str) -> AgentResponse:
        """Process a message and return a response. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process_message")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this agent."""
        total_requests = self._performance_metrics["requests_processed"]
        return {
            "agent_id": self.agent_id,
            "requests_processed": total_requests,
            "success_rate": (
                self._performance_metrics["success_count"] / total_requests 
                if total_requests > 0 else 0
            ),
            "average_execution_time": (
                self._performance_metrics["total_execution_time"] / total_requests
                if total_requests > 0 else 0
            ),
            "failure_count": self._performance_metrics["failure_count"]
        }
    
    def _update_metrics(self, success: bool, execution_time: float):
        """Update performance metrics after processing a message."""
        self._performance_metrics["requests_processed"] += 1
        self._performance_metrics["total_execution_time"] += execution_time
        
        if success:
            self._performance_metrics["success_count"] += 1
        else:
            self._performance_metrics["failure_count"] += 1


# Export for use by other modules
__all__ = ["AgentResponse", "BaseAgent"]