"""Base agent class for all AI agents in the clinical trials system."""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from openai import AsyncOpenAI
from app.core.config import get_settings


@dataclass
class AgentMessage:
    """Represents a message in agent conversation history."""
    
    role: str  # "user", "assistant", "system"
    content: str
    agent_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "role": self.role,
            "content": self.content,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class AgentResponse:
    """Represents a response from an agent."""
    
    success: bool
    content: str
    agent_id: str
    execution_time: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Base class for all AI agents in the clinical trials system."""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        model: str = "gpt-4",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ):
        """Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name of the agent
            description: Description of the agent's purpose
            model: OpenAI model to use
            temperature: Model temperature (0-2)
            max_tokens: Maximum tokens in response
            system_prompt: System prompt for the agent
        """
        if not agent_id:
            raise ValueError("Agent ID cannot be empty")
        
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
            
        if max_tokens <= 0:
            raise ValueError("Max tokens must be positive")
        
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        self.is_active = True
        self.message_history: List[AgentMessage] = []
        
        # Statistics tracking
        self._stats = {
            "message_count": 0,
            "total_execution_time": 0.0,
            "success_count": 0,
            "error_count": 0
        }
        
        # Initialize OpenAI client
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for the agent."""
        return f"You are {self.name}. {self.description}"
    
    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the conversation history."""
        self.message_history.append(message)
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.message_history.clear()
    
    def get_recent_messages(self, count: int) -> List[AgentMessage]:
        """Get the most recent messages from history."""
        return self.message_history[-count:] if count > 0 else []
    
    def activate(self) -> None:
        """Activate the agent."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the agent."""
        self.is_active = False
    
    def _build_messages_for_api(self, new_message: str) -> List[Dict[str, str]]:
        """Build messages list for OpenAI API call."""
        messages = []
        
        # Add system prompt
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # Add conversation history
        for msg in self.message_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add new user message
        messages.append({
            "role": "user",
            "content": new_message
        })
        
        return messages
    
    async def process_message(self, message: str, user_id: str = "user") -> AgentResponse:
        """Process a message and return a response.
        
        Args:
            message: The input message to process
            user_id: ID of the user sending the message
            
        Returns:
            AgentResponse with the result
        """
        start_time = time.time()
        
        # Check if agent is active
        if not self.is_active:
            return AgentResponse(
                success=False,
                content="",
                agent_id=self.agent_id,
                execution_time=0.0,
                error="Agent is not active"
            )
        
        try:
            # Build messages for API
            messages = self._build_messages_for_api(message)
            
            # Call OpenAI API
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract response
            response_content = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            
            execution_time = time.time() - start_time
            
            # Add messages to history
            self.add_message(AgentMessage(
                role="user",
                content=message,
                agent_id=user_id
            ))
            self.add_message(AgentMessage(
                role="assistant",
                content=response_content,
                agent_id=self.agent_id
            ))
            
            # Update statistics
            self._stats["message_count"] += 1
            self._stats["total_execution_time"] += execution_time
            self._stats["success_count"] += 1
            
            return AgentResponse(
                success=True,
                content=response_content,
                agent_id=self.agent_id,
                execution_time=execution_time,
                metadata={"tokens_used": tokens_used}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Update error statistics
            self._stats["message_count"] += 1
            self._stats["total_execution_time"] += execution_time
            self._stats["error_count"] += 1
            
            return AgentResponse(
                success=False,
                content="",
                agent_id=self.agent_id,
                execution_time=execution_time,
                error=str(e)
            )
    
    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Get agent statistics."""
        total_requests = self._stats["message_count"]
        success_rate = (
            (self._stats["success_count"] / total_requests * 100) 
            if total_requests > 0 else 0
        )
        average_execution_time = (
            (self._stats["total_execution_time"] / total_requests)
            if total_requests > 0 else 0
        )
        
        return {
            "message_count": self._stats["message_count"],
            "total_execution_time": self._stats["total_execution_time"],
            "average_execution_time": average_execution_time,
            "success_rate": success_rate,
            "success_count": self._stats["success_count"],
            "error_count": self._stats["error_count"]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "is_active": self.is_active,
            "message_count": len(self.message_history),
            "stats": self.get_stats()
        }


class ClinicalTrialsAgent(BaseAgent):
    """Specialized base class for clinical trials agents."""
    
    def __init__(self, **kwargs):
        """Initialize clinical trials agent with healthcare-specific defaults."""
        # Set healthcare-specific defaults
        kwargs.setdefault("temperature", 0.1)  # Lower temperature for accuracy
        kwargs.setdefault("max_tokens", 2000)  # Higher token limit for detailed responses
        
        super().__init__(**kwargs)
    
    def _get_default_system_prompt(self) -> str:
        """Get healthcare-specific system prompt."""
        return (
            f"You are {self.name}, an AI assistant specialized in clinical trials. "
            f"{self.description} "
            "You must provide accurate, evidence-based information and follow "
            "all applicable regulatory guidelines including ICH-GCP, FDA, and EMA standards. "
            "When in doubt, always err on the side of caution and recommend "
            "consulting with qualified medical professionals."
        )