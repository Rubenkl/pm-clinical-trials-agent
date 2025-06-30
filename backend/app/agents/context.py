"""OpenAI Agents SDK Context objects for state management.

This module implements Context objects that provide shared state between agents
in the multi-agent orchestration system using the OpenAI Agents SDK patterns.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorkflowContext:
    """Context object for sharing state between agents in a workflow.
    
    This follows the OpenAI Agents SDK pattern for dependency injection
    and shared state management across agent handoffs.
    """
    # User input and session
    user_request: str = ""
    session_id: str = ""
    user_id: Optional[str] = None
    
    # Workflow state
    workflow_state: str = "pending"  # pending, analyzing, verifying, completed, failed
    current_agent: str = ""
    previous_agents: List[str] = field(default_factory=list)
    
    # Analysis results
    query_analysis: Dict[str, Any] = field(default_factory=dict)
    data_verification: Dict[str, Any] = field(default_factory=dict)
    final_results: Dict[str, Any] = field(default_factory=dict)
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    
    def update_state(self, new_state: str, agent_name: str) -> None:
        """Update workflow state and track agent transitions."""
        self.previous_agents.append(self.current_agent) if self.current_agent else None
        self.current_agent = agent_name
        self.workflow_state = new_state
        self.updated_at = datetime.now()
    
    def add_error(self, error: str) -> None:
        """Add an error to the context."""
        self.errors.append(error)
        self.updated_at = datetime.now()
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the context."""
        self.warnings.append(warning)
        self.updated_at = datetime.now()
    
    def is_failed(self) -> bool:
        """Check if workflow has failed."""
        return self.workflow_state == "failed" or len(self.errors) > 0
    
    def is_completed(self) -> bool:
        """Check if workflow is completed successfully."""
        return self.workflow_state == "completed" and len(self.errors) == 0


@dataclass
class ClinicalTrialsContext(WorkflowContext):
    """Specialized context for clinical trials data management.
    
    Extends the base WorkflowContext with domain-specific state
    for clinical trials operations.
    """
    # Clinical trials specific data
    trial_id: Optional[str] = None
    protocol_data: Dict[str, Any] = field(default_factory=dict)
    participant_data: List[Dict[str, Any]] = field(default_factory=list)
    adverse_events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Compliance and validation
    regulatory_compliance: Dict[str, Any] = field(default_factory=dict)
    data_quality_scores: Dict[str, float] = field(default_factory=dict)
    validation_results: Dict[str, bool] = field(default_factory=dict)
    
    def add_participant(self, participant_data: Dict[str, Any]) -> None:
        """Add participant data to the context."""
        self.participant_data.append(participant_data)
        self.updated_at = datetime.now()
    
    def add_adverse_event(self, event_data: Dict[str, Any]) -> None:
        """Add adverse event data to the context."""
        self.adverse_events.append(event_data)
        self.updated_at = datetime.now()
    
    def update_compliance(self, compliance_type: str, status: bool, details: Dict[str, Any]) -> None:
        """Update regulatory compliance status."""
        self.regulatory_compliance[compliance_type] = {
            "status": status,
            "details": details,
            "updated_at": datetime.now()
        }
        self.updated_at = datetime.now()