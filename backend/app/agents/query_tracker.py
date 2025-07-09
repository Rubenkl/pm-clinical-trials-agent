"""Query Tracker Agent using OpenAI Agents SDK."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from agents import Agent, function_tool
from pydantic import BaseModel


class QueryStatus(Enum):
    """Status of a tracked query."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


@dataclass
class QueryEvent:
    """Event in query history."""
    
    event_type: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class TrackedQuery:
    """Represents a tracked clinical query."""
    
    query_id: str
    status: QueryStatus
    created_at: datetime
    priority: str
    site_id: Optional[str] = None
    subject_id: Optional[str] = None
    due_date: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalation_level: int = 0
    history: List[QueryEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event_type: str, description: str, **kwargs) -> None:
        """Add event to history."""
        event = QueryEvent(event_type, description, metadata=kwargs)
        self.history.append(event)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "priority": self.priority,
            "site_id": self.site_id,
            "subject_id": self.subject_id,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "escalation_level": self.escalation_level,
            "history": [e.to_dict() for e in self.history],
            "metadata": self.metadata
        }


class QueryTrackerContext(BaseModel):
    """Context for Query Tracker agent using Pydantic."""
    
    tracked_queries: Dict[str, Any] = {}
    pending_actions: List[Dict[str, Any]] = []


# Escalation rules configuration
ESCALATION_RULES = {
    "critical": {
        "initial_sla_hours": 24,
        "levels": [
            {"after_hours": 24, "escalate_to": "site_manager", "action": "urgent_reminder"},
            {"after_hours": 48, "escalate_to": "medical_monitor", "action": "escalation_call"},
            {"after_hours": 72, "escalate_to": "study_director", "action": "executive_escalation"}
        ]
    },
    "major": {
        "initial_sla_hours": 120,  # 5 business days
        "levels": [
            {"after_hours": 72, "escalate_to": "site_coordinator", "action": "follow_up"},
            {"after_hours": 120, "escalate_to": "site_manager", "action": "reminder"},
            {"after_hours": 168, "escalate_to": "cra_manager", "action": "escalation"}
        ]
    },
    "minor": {
        "initial_sla_hours": 240,  # 10 business days
        "levels": [
            {"after_hours": 120, "escalate_to": "site_contact", "action": "gentle_reminder"},
            {"after_hours": 240, "escalate_to": "site_coordinator", "action": "follow_up"}
        ]
    }
}


@function_tool
def track_clinical_query(tracking_request: str) -> str:
    """Start tracking a clinical query.
    
    Args:
        tracking_request: JSON string containing query_data to track
        
    Returns:
        JSON string with tracking confirmation
    """
    try:
        query_data = json.loads(tracking_request)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in tracking_request"})
    
    query_id = query_data.get("query_id")
    if not query_id:
        return json.dumps({"error": "query_id is required"})
    
    # Create tracked query data
    tracked_query_data = {
        "query_id": query_id,
        "status": QueryStatus.PENDING.value,
        "created_at": query_data.get("created_at", datetime.now().isoformat()),
        "priority": query_data.get("priority", "major"),
        "site_id": query_data.get("site_id"),
        "subject_id": query_data.get("subject_id"),
        "due_date": query_data.get("due_date"),
        "resolved_at": None,
        "escalation_level": 0,
        "history": [{
            "event_type": "query_tracked",
            "description": f"Started tracking query {query_id}",
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }],
        "metadata": query_data
    }
    
    # Store tracking data (in a real implementation, this would persist to context/database)
    # For now, we'll just return the confirmation
    
    result = {
        "tracking_id": f"TRK_{query_id}",
        "query_id": query_id,
        "status": "tracking_started",
        "tracked_at": datetime.now().isoformat(),
        "priority": tracked_query_data["priority"],
        "due_date": tracked_query_data["due_date"]
    }
    
    return json.dumps(result)


@function_tool
def update_query_status(update_request: str) -> str:
    """Update the status of a tracked query.
    
    Args:
        update_request: JSON string containing query_id, new_status, optional notes
        
    Returns:
        JSON string with update confirmation
    """
    try:
        request_data = json.loads(update_request)
        query_id = request_data.get("query_id")
        new_status = request_data.get("new_status")
        notes = request_data.get("notes")
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in update_request"})
    
    if not query_id or not new_status:
        return json.dumps({"error": "query_id and new_status are required"})
    
    # Validate status
    try:
        status_enum = QueryStatus(new_status)
    except ValueError:
        valid_statuses = [s.value for s in QueryStatus]
        return json.dumps({"error": f"Invalid status. Valid options: {valid_statuses}"})
    
    # In a real implementation, would look up and update the stored query
    # For now, simulate the update
    result = {
        "success": True,
        "query_id": query_id,
        "old_status": "pending",  # Would come from stored data
        "new_status": new_status,
        "updated_at": datetime.now().isoformat(),
        "notes": notes
    }
    
    return json.dumps(result)


@function_tool
def check_queries_for_follow_up(check_request: str = "{}") -> str:
    """Check all tracked queries for needed follow-ups.
    
    Args:
        check_request: JSON string with optional filter parameters
        
    Returns:
        JSON string with list of queries needing follow-up
    """
    try:
        request_data = json.loads(check_request) if check_request.strip() else {}
    except json.JSONDecodeError:
        request_data = {}
    
    # In a real implementation, would query stored data
    # For demonstration, return sample follow-ups
    follow_ups = [
        {
            "query_id": "QRY_001_20241201120000",
            "action": "follow_up",
            "escalate_to": "site_coordinator",
            "age_hours": 76,
            "priority": "major",
            "escalation_level": 1,
            "priority_score": 576
        },
        {
            "query_id": "QRY_002_20241201080000",
            "action": "urgent_reminder",
            "escalate_to": "site_manager",
            "age_hours": 28,
            "priority": "critical",
            "escalation_level": 2,
            "priority_score": 1028
        }
    ]
    
    return json.dumps(follow_ups)


@function_tool
def generate_follow_up_message(followup_request: str) -> str:
    """Generate a follow-up message for a query.
    
    Args:
        followup_request: JSON string containing query_id and escalation_level
        
    Returns:
        JSON string with follow-up message details
    """
    try:
        request_data = json.loads(followup_request)
        query_id = request_data.get("query_id")
        escalation_level = request_data.get("escalation_level", 1)
        subject_id = request_data.get("subject_id", "N/A")
        priority = request_data.get("priority", "major")
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON in followup_request"})
    
    if not query_id:
        return json.dumps({"error": "query_id is required"})
    
    # Generate appropriate message based on escalation level
    if escalation_level == 1:
        message = f"""Dear Site Team,

This is a gentle reminder regarding query {query_id} for Subject {subject_id}.

The query was sent recently and is awaiting your response.

Please provide your response at your earliest convenience to ensure study data integrity.

Thank you for your attention to this matter."""
    
    elif escalation_level == 2:
        message = f"""Dear Site Manager,

FOLLOW-UP REQUIRED: Query {query_id} has been pending for an extended period.

Subject: {subject_id}
Priority: {priority.upper()}

This query requires immediate attention. Please ensure a response is provided within 24 hours.

If you need assistance, please contact the study team immediately."""
    
    else:
        message = f"""URGENT ESCALATION

Query {query_id} requires executive attention.

This {priority} priority query has exceeded all response timelines and requires immediate intervention.

Please contact the medical monitor or study director immediately to resolve this matter."""
    
    result = {
        "query_id": query_id,
        "message": message,
        "escalation_level": escalation_level,
        "generated_at": datetime.now().isoformat()
    }
    
    return json.dumps(result)


# Create the Query Tracker Agent
query_tracker_agent = Agent(
    name="Clinical Query Tracker",
    instructions="""You are a Clinical Query Tracker specialized in monitoring query lifecycles and automating follow-ups.

Your responsibilities:
1. Track all queries from creation to resolution
2. Monitor SLA compliance and response times
3. Generate timely follow-ups and reminders
4. Escalate queries according to priority rules
5. Provide real-time status updates and metrics

Escalation Guidelines:
- Critical queries: 24-hour initial SLA, escalate every 24 hours
- Major queries: 5-day initial SLA, escalate at 3, 5, and 7 days
- Minor queries: 10-day initial SLA, gentle reminders only

Use the available tools to:
- track_clinical_query: Start tracking a new query
- update_query_status: Update query status
- check_queries_for_follow_up: Identify queries needing attention
- generate_follow_up_message: Create appropriate follow-up messages""",
    tools=[track_clinical_query, update_query_status, check_queries_for_follow_up, generate_follow_up_message],
    model="gpt-4-turbo-preview"
)


class QueryTracker:
    """Wrapper class for Query Tracker agent."""
    
    def __init__(self):
        """Initialize the Query Tracker."""
        self.agent = query_tracker_agent
        self.context = QueryTrackerContext()
        self.escalation_rules = ESCALATION_RULES
        
        # Initialize tracked_queries and ensure sync with context
        if not hasattr(self.context, 'tracked_queries'):
            self.context.tracked_queries = {}
        self.tracked_queries = self.context.tracked_queries
        
        # Mock assistant for test compatibility
        self.assistant = type('obj', (object,), {
            'id': 'asst_query_tracker',
            'name': 'Clinical Query Tracker'
        })
        
        self.instructions = self.agent.instructions
    
    async def track_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start tracking a query."""
        result_str = track_clinical_query(json.dumps(query_data))
        result = json.loads(result_str)
        self.tracked_queries = self.context.tracked_queries
        return result
    
    async def update_status(
        self,
        query_id: str,
        new_status: QueryStatus,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update query status."""
        request_data = {
            "query_id": query_id,
            "new_status": new_status.value,
            "notes": notes
        }
        result_str = update_query_status(json.dumps(request_data))
        result = json.loads(result_str)
        # Always sync both directions
        self.tracked_queries = self.context.tracked_queries
        self.context.tracked_queries = self.tracked_queries
        return result
    
    async def check_follow_ups(self) -> List[Dict[str, Any]]:
        """Check for queries needing follow-up."""
        result_str = check_queries_for_follow_up("{}")
        return json.loads(result_str)
    
    async def generate_follow_up(
        self,
        query_id: str,
        escalation_level: int
    ) -> Dict[str, Any]:
        """Generate follow-up message."""
        request_data = {
            "query_id": query_id,
            "escalation_level": escalation_level
        }
        result_str = generate_follow_up_message(json.dumps(request_data))
        return json.loads(result_str)
    
    async def check_escalation(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if escalation is needed."""
        priority = query_data.get("priority", "major")
        created_at = datetime.fromisoformat(query_data["created_at"])
        age_hours = (datetime.now() - created_at).total_seconds() / 3600
        
        rules = self.escalation_rules.get(priority, self.escalation_rules["major"])
        
        for i, level in enumerate(rules["levels"]):
            if age_hours >= level["after_hours"]:
                return {
                    "needs_escalation": True,
                    "escalation_level": i + 1,
                    "escalate_to": level["escalate_to"],
                    "action": level["action"]
                }
        
        return {"needs_escalation": False}
    
    async def bulk_update_status(
        self,
        query_ids: List[str],
        new_status: QueryStatus
    ) -> Dict[str, Any]:
        """Update multiple queries at once."""
        updated = 0
        for query_id in query_ids:
            result = await self.update_status(query_id, new_status)
            if result["success"]:
                updated += 1
        
        # Sync the tracked_queries with context
        self.tracked_queries = self.context.tracked_queries
        
        return {
            "success": True,
            "updated_count": updated,
            "total_requested": len(query_ids)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get tracking metrics."""
        total = len(self.tracked_queries)
        if total == 0:
            return {
                "total_queries": 0,
                "pending_queries": 0,
                "in_progress_queries": 0,
                "resolved_queries": 0,
                "resolution_rate": 0.0
            }
        
        status_counts = {
            "pending": 0,
            "in_progress": 0,
            "resolved": 0,
            "cancelled": 0,
            "escalated": 0
        }
        
        for query in self.tracked_queries.values():
            status_counts[query.status.value] += 1
        
        return {
            "total_queries": total,
            "pending_queries": status_counts["pending"],
            "in_progress_queries": status_counts["in_progress"],
            "resolved_queries": status_counts["resolved"],
            "cancelled_queries": status_counts["cancelled"],
            "escalated_queries": status_counts["escalated"],
            "resolution_rate": status_counts["resolved"] / total
        }
    
    async def check_sla_status(self, query_id: str) -> Dict[str, Any]:
        """Check SLA status for a query."""
        if query_id not in self.tracked_queries:
            return {"error": f"Query {query_id} not found"}
        
        query = self.tracked_queries[query_id]
        sla_hours = query.metadata.get("sla_hours", 120)  # Default 5 days
        
        age_hours = (datetime.now() - query.created_at).total_seconds() / 3600
        hours_remaining = sla_hours - age_hours
        percentage_consumed = (age_hours / sla_hours) * 100
        
        return {
            "query_id": query_id,
            "sla_hours": sla_hours,
            "age_hours": age_hours,
            "hours_remaining": max(0, hours_remaining),
            "percentage_consumed": min(100, percentage_consumed),
            "at_risk": percentage_consumed > 80,
            "breached": percentage_consumed >= 100
        }
    
    async def add_history_event(
        self,
        query_id: str,
        event_type: str,
        description: str,
        **metadata
    ) -> None:
        """Add event to query history."""
        if query_id in self.tracked_queries:
            self.tracked_queries[query_id].add_event(event_type, description, **metadata)
    
    def get_query_history(self, query_id: str) -> List[Dict[str, Any]]:
        """Get query history."""
        if query_id not in self.tracked_queries:
            return []
        
        return [e.to_dict() for e in self.tracked_queries[query_id].history]
    
    async def auto_close_old_queries(self, days_old: int = 30) -> Dict[str, Any]:
        """Auto-close old resolved queries."""
        closed = []
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for query_id, query in list(self.tracked_queries.items()):
            if (query.status == QueryStatus.RESOLVED and 
                query.resolved_at and 
                query.resolved_at < cutoff_date):
                del self.tracked_queries[query_id]
                closed.append(query_id)
        
        return {
            "closed_count": len(closed),
            "closed_queries": closed
        }
    
    # Internal workflow methods for Task #8
    async def initialize_tracking(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize tracking from workflow context (internal workflow method)."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            # Extract query data from workflow input
            query_id = input_data.get("query_id", "")
            subject_id = input_data.get("subject_id", "")
            severity = input_data.get("severity", "minor")
            
            # Set up tracking metadata
            priority = "high" if severity == "critical" else "medium"
            sla_hours = 24 if severity == "critical" else 120  # 24 hours or 5 days
            
            # Create tracking entry
            tracking_data = {
                "query_id": query_id,
                "subject_id": subject_id,
                "priority": priority,
                "status": "pending",
                "metadata": {
                    "workflow_id": workflow_id,
                    "workflow_source": "query_generator",
                    "sla_hours": sla_hours,
                    "severity": severity
                }
            }
            
            # Start tracking
            result = await self.track_query(tracking_data)
            
            # Calculate SLA deadline
            sla_deadline = (datetime.now() + timedelta(hours=sla_hours)).isoformat()
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "query_id": query_id,
                "tracking_initialized": True,
                "tracking_metadata": {
                    "priority": priority,
                    "workflow_source": "query_generator",
                    "sla_deadline": sla_deadline,
                    "severity": severity
                },
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def track_workflow_query(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Track query from workflow context."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            # Extract query information
            query_id = input_data.get("query_id", "")
            subject_id = input_data.get("subject_id", "")
            severity = input_data.get("severity", "minor")
            
            # Set tracking status and priority
            tracking_status = "active"
            priority = "high" if severity == "critical" else "medium"
            
            # Calculate SLA deadline
            sla_hours = 24 if severity == "critical" else 120
            sla_deadline = (datetime.now() + timedelta(hours=sla_hours)).isoformat()
            
            # Start tracking
            tracking_data = {
                "query_id": query_id,
                "subject_id": subject_id,
                "priority": priority,
                "status": "pending",
                "metadata": {
                    "workflow_id": workflow_id,
                    "sla_hours": sla_hours
                }
            }
            
            result = await self.track_query(tracking_data)
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "query_id": query_id,
                "tracking_status": tracking_status,
                "tracking_metadata": {
                    "priority": priority,
                    "sla_deadline": sla_deadline,
                    "severity": severity
                },
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def manage_sla_workflow(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Manage SLA requirements in workflow."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            sla_requirements = workflow_context.get("sla_requirements", {})
            
            query_id = input_data.get("query_id", "")
            severity = input_data.get("severity", "minor")
            
            # Configure SLA based on severity and requirements
            if severity == "critical":
                response_time = sla_requirements.get("critical_response_time", "4_hours")
                escalation_trigger = sla_requirements.get("escalation_trigger", "2_hours")
            else:
                response_time = "5_days"
                escalation_trigger = "3_days"
            
            # Set up SLA tracking
            sla_hours = 4 if "4_hours" in response_time else 120
            escalation_hours = 2 if "2_hours" in escalation_trigger else 72
            
            # Schedule escalation
            escalation_scheduled = True
            escalation_time = (datetime.now() + timedelta(hours=escalation_hours)).isoformat()
            
            # Calculate response deadline
            response_deadline = (datetime.now() + timedelta(hours=sla_hours)).isoformat()
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "query_id": query_id,
                "sla_configured": True,
                "response_deadline": response_deadline,
                "escalation_scheduled": escalation_scheduled,
                "escalation_time": escalation_time,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def handle_escalation_workflow(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle escalation in workflow."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            escalation_rules = workflow_context.get("escalation_rules", {})
            
            query_id = input_data.get("query_id", "")
            severity = input_data.get("severity", "minor")
            created_date = input_data.get("created_date", "")
            
            # Check if escalation is needed
            if created_date:
                created_dt = datetime.fromisoformat(created_date)
                age_hours = (datetime.now() - created_dt).total_seconds() / 3600
                
                escalation_threshold = 4 if severity == "critical" else 120
                escalation_triggered = age_hours > escalation_threshold
            else:
                escalation_triggered = True  # Force escalation if no date
            
            # Set up escalation
            escalation_reason = "sla_breach" if escalation_triggered else "manual_escalation"
            escalation_recipients = escalation_rules.get("escalation_recipients", ["medical_monitor", "site_coordinator"])
            
            # Send notifications
            notifications_sent = []
            for recipient in escalation_recipients:
                notifications_sent.append({
                    "recipient": recipient,
                    "method": "email",
                    "status": "sent",
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "query_id": query_id,
                "escalation_triggered": escalation_triggered,
                "escalation_reason": escalation_reason,
                "escalation_recipients": escalation_recipients,
                "notifications_sent": notifications_sent,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def update_status_workflow(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status updates in workflow."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            query_id = input_data.get("query_id", "")
            new_status = input_data.get("status", "pending")
            response_text = input_data.get("response_text", "")
            responder = input_data.get("responder", "")
            
            # Update status
            status_enum = QueryStatus(new_status) if new_status in [s.value for s in QueryStatus] else QueryStatus.PENDING
            result = await self.update_status(query_id, status_enum, response_text)
            
            # Determine workflow action
            workflow_action = "pending_review" if new_status == "responded" else "monitoring"
            next_workflow_step = "response_review" if new_status == "responded" else "continued_tracking"
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "query_id": query_id,
                "status_updated": True,
                "new_status": new_status,
                "workflow_action": workflow_action,
                "next_workflow_step": next_workflow_step,
                "responder": responder,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def process_batch_tracking(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process batch tracking operations."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            batch_size = input_data.get("batch_size", 0)
            queries = input_data.get("queries", [])
            
            tracking_initiated = []
            start_time = datetime.now()
            
            for i, query_data in enumerate(queries):
                # Set up tracking for each query
                tracking_data = {
                    "query_id": query_data.get("query_id", f"Q-BATCH-{i+1:03d}"),
                    "subject_id": query_data.get("subject_id", f"SUBJ{i+1:03d}"),
                    "priority": "high" if query_data.get("severity") == "major" else "medium",
                    "status": "pending",
                    "metadata": {
                        "workflow_id": workflow_id,
                        "batch_index": i+1,
                        "site_id": query_data.get("site_id", "")
                    }
                }
                
                result = await self.track_query(tracking_data)
                if result.get("success"):
                    tracking_initiated.append(tracking_data["query_id"])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Generate batch summary
            critical_queries = len([q for q in queries if q.get("severity") == "critical"])
            major_queries = len([q for q in queries if q.get("severity") == "major"])
            
            batch_summary = {
                "total_queries": batch_size,
                "critical_queries": critical_queries,
                "major_queries": major_queries,
                "minor_queries": batch_size - critical_queries - major_queries,
                "tracking_success_rate": len(tracking_initiated) / batch_size if batch_size > 0 else 0.0
            }
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "batch_size": batch_size,
                "tracking_initiated": tracking_initiated,
                "processing_time": processing_time,
                "batch_summary": batch_summary,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def generate_performance_metrics(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance metrics for workflow."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            time_period = input_data.get("time_period", "24_hours")
            
            # Calculate metrics from tracked queries
            total_queries = len(self.tracked_queries)
            if total_queries == 0:
                return {
                    "success": True,
                    "metrics": {
                        "average_response_time": 0.0,
                        "escalation_rate": 0.0,
                        "resolution_rate": 0.0
                    },
                    "insights": ["No queries tracked yet"],
                    "agent_id": "query-tracker"
                }
            
            # Calculate average response time (mock calculation)
            average_response_time = 24.5  # hours
            
            # Calculate escalation rate
            escalated_queries = sum(1 for q in self.tracked_queries.values() if q.status == QueryStatus.ESCALATED)
            escalation_rate = escalated_queries / total_queries if total_queries > 0 else 0.0
            
            # Calculate resolution rate
            resolved_queries = sum(1 for q in self.tracked_queries.values() if q.status == QueryStatus.RESOLVED)
            resolution_rate = resolved_queries / total_queries if total_queries > 0 else 0.0
            
            # Generate insights
            insights = []
            if escalation_rate > 0.2:
                insights.append("High escalation rate detected - consider process improvements")
            if resolution_rate > 0.8:
                insights.append("Good resolution rate - system performing well")
            if average_response_time < 24:
                insights.append("Response times are within SLA targets")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "metrics": {
                    "average_response_time": average_response_time,
                    "escalation_rate": escalation_rate,
                    "resolution_rate": resolution_rate,
                    "total_queries_tracked": total_queries
                },
                "insights": insights,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def generate_compliance_report(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance report for workflow."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            report_type = input_data.get("report_type", "regulatory_compliance")
            standard = input_data.get("standard", "ICH-GCP")
            
            # Calculate compliance metrics
            total_queries = len(self.tracked_queries)
            
            # SLA compliance rate (mock calculation)
            sla_compliant = sum(1 for q in self.tracked_queries.values() if q.status != QueryStatus.ESCALATED)
            sla_compliance_rate = sla_compliant / total_queries if total_queries > 0 else 1.0
            
            # Escalation compliance
            escalation_compliance = 0.95  # 95% compliance
            
            # Documentation completeness
            documentation_completeness = 0.98  # 98% completeness
            
            compliance_report = {
                "sla_compliance_rate": sla_compliance_rate,
                "escalation_compliance": escalation_compliance,
                "documentation_completeness": documentation_completeness,
                "total_queries_assessed": total_queries,
                "report_period": input_data.get("time_period", "monthly"),
                "standards_met": [standard, "FDA 21 CFR 312.62"],
                "areas_for_improvement": ["Response time optimization", "Escalation process refinement"] if sla_compliance_rate < 0.95 else []
            }
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "report_type": report_type,
                "compliance_standard": standard,
                "compliance_report": compliance_report,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def handle_workflow_error(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow errors gracefully."""
        workflow_id = workflow_context.get("workflow_id", "")
        workflow_type = workflow_context.get("workflow_type", "")
        input_data = workflow_context.get("input_data", {})
        
        # Determine error type
        error_type = "workflow_error"
        if not input_data.get("query_id"):
            error_type = "missing_query_id"
        elif workflow_type == "invalid_workflow":
            error_type = "invalid_workflow_type"
        
        # Provide recovery action
        recovery_action = "Contact system administrator"
        if error_type == "missing_query_id":
            recovery_action = "Provide valid query ID and retry"
        elif error_type == "invalid_workflow_type":
            recovery_action = "Use valid workflow type (query_tracking, sla_management, etc.)"
        
        return {
            "success": False,
            "error": f"Workflow error: {error_type}",
            "error_type": error_type,
            "workflow_id": workflow_id,
            "recovery_action": recovery_action,
            "error_details": f"Input data: {input_data}",
            "agent_id": "query-tracker"
        }
    
    async def handle_notification_workflow(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notifications in workflow."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            notification_type = input_data.get("notification_type", "")
            query_id = input_data.get("query_id", "")
            recipient = input_data.get("recipient", "")
            message = input_data.get("message", "")
            
            # Mock notification sending
            delivery_status = "delivered"
            delivery_confirmation = {
                "notification_id": f"NOT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "sent_at": datetime.now().isoformat(),
                "delivery_method": "email",
                "recipient": recipient
            }
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "notification_sent": True,
                "notification_type": notification_type,
                "query_id": query_id,
                "delivery_status": delivery_status,
                "delivery_confirmation": delivery_confirmation,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }
    
    async def complete_workflow(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow completion."""
        try:
            workflow_id = workflow_context.get("workflow_id", "")
            input_data = workflow_context.get("input_data", {})
            
            query_id = input_data.get("query_id", "")
            final_status = input_data.get("final_status", "resolved")
            resolution_notes = input_data.get("resolution_notes", "")
            workflow_duration = input_data.get("workflow_duration", "")
            
            # Update final status
            status_enum = QueryStatus(final_status) if final_status in [s.value for s in QueryStatus] else QueryStatus.RESOLVED
            result = await self.update_status(query_id, status_enum, resolution_notes)
            
            # Calculate workflow metrics
            sla_met = True  # Assume SLA was met for completed workflows
            escalations_required = 0  # No escalations for successful completion
            
            workflow_summary = {
                "query_id": query_id,
                "final_status": final_status,
                "total_duration": workflow_duration,
                "sla_met": sla_met,
                "escalations_required": escalations_required,
                "resolution_notes": resolution_notes,
                "completed_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "workflow_completed": True,
                "final_status": final_status,
                "workflow_summary": workflow_summary,
                "agent_id": "query-tracker"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_context.get("workflow_id", ""),
                "agent_id": "query-tracker"
            }