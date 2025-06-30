"""OpenAI Agents SDK handoff and delegation patterns.

This module implements the handoff mechanisms that enable agents to delegate
tasks to specialized sub-agents using the OpenAI Agents SDK patterns.
"""

import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
import re

from app.agents.context import WorkflowContext, ClinicalTrialsContext


@dataclass
class HandoffDefinition:
    """Definition of a handoff between agents.
    
    This represents a potential handoff that can be executed when certain
    conditions are met in the workflow context.
    """
    name: str
    target_agent: str
    description: str
    condition_func: Callable[[WorkflowContext], bool]
    priority: int = 1
    timeout: float = 30.0
    
    def should_execute(self, context: WorkflowContext) -> bool:
        """Check if this handoff should be executed for the given context."""
        try:
            return self.condition_func(context)
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert handoff definition to dictionary format."""
        return {
            "name": self.name,
            "target_agent": self.target_agent,
            "description": self.description,
            "priority": self.priority,
            "timeout": self.timeout
        }
    
    def __gt__(self, other):
        """Compare handoffs by priority (higher priority > lower priority)."""
        return self.priority > other.priority
    
    def __lt__(self, other):
        """Compare handoffs by priority (lower priority < higher priority)."""
        return self.priority < other.priority


@dataclass
class AgentHandoff:
    """Represents an actual handoff execution between agents."""
    source_agent: str
    target_agent: str
    handoff_context: Dict[str, Any]
    status: str = "pending"  # pending, in_progress, completed, failed, timeout
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    
    def mark_started(self) -> None:
        """Mark handoff as started."""
        self.status = "in_progress"
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Dict[str, Any]) -> None:
        """Mark handoff as completed with result."""
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.now()
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
        else:
            self.execution_time = (self.completed_at - self.created_at).total_seconds()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark handoff as failed with error message."""
        self.status = "failed"
        self.error_message = error_message
        self.completed_at = datetime.now()
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
        else:
            self.execution_time = (self.completed_at - self.created_at).total_seconds()
    
    def mark_timeout(self) -> None:
        """Mark handoff as timed out."""
        self.status = "timeout"
        self.error_message = "Handoff execution exceeded timeout limit"
        self.completed_at = datetime.now()
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
        else:
            self.execution_time = (self.completed_at - self.created_at).total_seconds()


class HandoffRegistry:
    """Registry for managing handoff definitions and execution."""
    
    def __init__(self):
        self.handoffs: List[HandoffDefinition] = []
        self.execution_history: List[AgentHandoff] = []
    
    def register_handoff(self, handoff: HandoffDefinition) -> None:
        """Register a handoff definition."""
        self.handoffs.append(handoff)
        # Sort by priority (highest first)
        self.handoffs.sort(reverse=True)
    
    def find_applicable_handoffs(self, context: WorkflowContext) -> List[HandoffDefinition]:
        """Find all handoffs applicable to the given context, sorted by priority."""
        applicable = []
        for handoff in self.handoffs:
            if handoff.should_execute(context):
                applicable.append(handoff)
        
        # Sort by priority (highest first)
        applicable.sort(reverse=True)
        return applicable
    
    def execute_handoff(
        self, 
        handoff_def: HandoffDefinition, 
        context: WorkflowContext,
        agent_func: Callable[[WorkflowContext, Dict[str, Any]], Dict[str, Any]]
    ) -> AgentHandoff:
        """Execute a handoff to the target agent."""
        # Create handoff execution record
        handoff = AgentHandoff(
            source_agent=context.current_agent,
            target_agent=handoff_def.target_agent,
            handoff_context=handoff_def.to_dict()
        )
        
        try:
            handoff.mark_started()
            
            # Execute the agent function
            result = agent_func(context, handoff_def.to_dict())
            handoff.mark_completed(result)
            
        except Exception as e:
            handoff.mark_failed(str(e))
        
        # Add to execution history
        self.execution_history.append(handoff)
        return handoff
    
    def get_execution_history(
        self, 
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[AgentHandoff]:
        """Get execution history with optional filtering."""
        history = self.execution_history
        
        if source_agent:
            history = [h for h in history if h.source_agent == source_agent]
        
        if target_agent:
            history = [h for h in history if h.target_agent == target_agent]
        
        if status:
            history = [h for h in history if h.status == status]
        
        return history


class QueryAnalyzerHandoff(HandoffDefinition):
    """Specialized handoff for Query Analyzer agent."""
    
    def __init__(self):
        super().__init__(
            name="query_analyzer_handoff",
            target_agent="QueryAnalyzer",
            description="Hand off to Query Analyzer for user query analysis and intent detection",
            condition_func=self._should_analyze_query,
            priority=5
        )
    
    def _should_analyze_query(self, context: WorkflowContext) -> bool:
        """Determine if query analysis is needed."""
        if not context.user_request:
            return False
        
        # Keywords that indicate query analysis is needed
        query_keywords = [
            "show", "find", "get", "what", "how", "when", "where", "which",
            "analyze", "analysis", "report", "status", "data", "information",
            "enrollment", "adverse", "trial", "participant", "protocol"
        ]
        
        request_lower = context.user_request.lower()
        
        # First, exclude casual greetings and social interactions
        social_patterns = [
            r'^(hello|hi|hey)\b',
            r'\bhow are you\b',
            r'\bhow\'s it going\b',
            r'^(good morning|good afternoon|good evening)\b'
        ]
        
        for pattern in social_patterns:
            if re.search(pattern, request_lower):
                return False
        
        # Check if request contains query-related keywords
        for keyword in query_keywords:
            if keyword in request_lower:
                return True
        
        # Check if request contains question patterns
        question_patterns = [
            r'\?',  # Contains question mark
            r'^(what|how|when|where|which|who|why)\s',  # Starts with question words
            r'\b(is|are|was|were|can|could|will|would|should|do|does|did)\s'  # Question auxiliaries
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, request_lower):
                return True
        
        return False
    
    def prepare_handoff_context(self, context: WorkflowContext) -> Dict[str, Any]:
        """Prepare context for Query Analyzer handoff."""
        return {
            "query": context.user_request,
            "session_id": context.session_id,
            "user_id": context.user_id,
            "analysis_type": "user_query",
            "workflow_state": context.workflow_state,
            "timestamp": datetime.now().isoformat()
        }


class DataVerifierHandoff(HandoffDefinition):
    """Specialized handoff for Data Verifier agent."""
    
    def __init__(self):
        super().__init__(
            name="data_verifier_handoff",
            target_agent="DataVerifier",
            description="Hand off to Data Verifier for data verification and validation",
            condition_func=self._should_verify_data,
            priority=8
        )
    
    def _should_verify_data(self, context: WorkflowContext) -> bool:
        """Determine if data verification is needed."""
        # Check if query analysis indicates verification is needed
        if hasattr(context, 'query_analysis') and context.query_analysis:
            return context.query_analysis.get('requires_verification', False)
        
        return False
    
    def prepare_handoff_context(self, context: WorkflowContext) -> Dict[str, Any]:
        """Prepare context for Data Verifier handoff."""
        handoff_context = {
            "verification_type": "data_quality",
            "timestamp": datetime.now().isoformat()
        }
        
        # Add query analysis results if available
        if hasattr(context, 'query_analysis') and context.query_analysis:
            handoff_context.update({
                "data_sources": context.query_analysis.get('data_sources', []),
                "verification_entities": context.query_analysis.get('entities', []),
                "analysis_confidence": context.query_analysis.get('confidence', 0.0)
            })
        
        # Add clinical trial specific context if applicable
        if isinstance(context, ClinicalTrialsContext):
            handoff_context.update({
                "trial_id": context.trial_id,
                "participant_count": len(context.participant_data),
                "adverse_events_count": len(context.adverse_events)
            })
        
        return handoff_context