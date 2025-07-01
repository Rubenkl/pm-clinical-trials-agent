"""Handoff Registry for OpenAI Agents SDK Integration."""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Import all SDK agents
from app.agents.portfolio_manager import (
    PortfolioManager, 
    WorkflowContext,
    portfolio_manager_agent
)
from app.agents.query_analyzer import (
    QueryAnalyzer,
    QueryAnalysisContext, 
    query_analyzer_agent
)
from app.agents.query_generator import (
    QueryGenerator,
    QueryGeneratorContext,
    query_generator_agent
)
from app.agents.query_tracker import (
    QueryTracker,
    QueryTrackerContext,
    query_tracker_agent
)
from app.agents.data_verifier import (
    DataVerifier,
    DataVerificationContext,
    data_verifier_agent
)

# OpenAI Agents SDK imports
try:
    from openai_agents import Agent, Context, Handoff
except ImportError:
    # Mock for development
    class Handoff:
        def __init__(self, target_agent, name, condition=None, context_transfer=None):
            self.target_agent = target_agent
            self.name = name
            self.condition = condition
            self.context_transfer = context_transfer or []


class AgentRole(Enum):
    """Roles of agents in the clinical trials system."""
    
    PORTFOLIO_MANAGER = "portfolio_manager"
    QUERY_ANALYZER = "query_analyzer"
    QUERY_GENERATOR = "query_generator"
    QUERY_TRACKER = "query_tracker"
    DATA_VERIFIER = "data_verifier"


@dataclass
class HandoffRule:
    """Defines a handoff rule between agents."""
    
    from_agent: AgentRole
    to_agent: AgentRole
    condition: str
    context_transfer: List[str]
    priority: int = 1
    description: str = ""


class ClinicalTrialsHandoffRegistry:
    """Registry for managing handoffs between clinical trials agents."""
    
    def __init__(self):
        """Initialize the handoff registry with all agents and rules."""
        
        # Initialize all agents
        self.agents = {
            AgentRole.PORTFOLIO_MANAGER: PortfolioManager(),
            AgentRole.QUERY_ANALYZER: QueryAnalyzer(),
            AgentRole.QUERY_GENERATOR: QueryGenerator(),
            AgentRole.QUERY_TRACKER: QueryTracker(),
            AgentRole.DATA_VERIFIER: DataVerifier()
        }
        
        # Define handoff rules
        self.handoff_rules = self._define_handoff_rules()
        
        # Create OpenAI SDK handoff objects
        self.sdk_handoffs = self._create_sdk_handoffs()
        
        # Register handoffs with agents
        self._register_handoffs()
    
    def _define_handoff_rules(self) -> List[HandoffRule]:
        """Define all handoff rules between agents."""
        
        return [
            # Portfolio Manager to Query Analyzer
            HandoffRule(
                from_agent=AgentRole.PORTFOLIO_MANAGER,
                to_agent=AgentRole.QUERY_ANALYZER,
                condition="when clinical data needs analysis for discrepancies",
                context_transfer=["data_points", "trial_metadata", "analysis_requirements"],
                priority=1,
                description="Hand off data analysis tasks to specialized query analyzer"
            ),
            
            # Portfolio Manager to Data Verifier
            HandoffRule(
                from_agent=AgentRole.PORTFOLIO_MANAGER,
                to_agent=AgentRole.DATA_VERIFIER,
                condition="when cross-system data verification is needed",
                context_transfer=["edc_data", "source_data", "verification_requirements"],
                priority=1,
                description="Hand off data verification tasks to specialized verifier"
            ),
            
            # Query Analyzer to Query Generator
            HandoffRule(
                from_agent=AgentRole.QUERY_ANALYZER,
                to_agent=AgentRole.QUERY_GENERATOR,
                condition="when analysis results need to be converted to clinical queries",
                context_transfer=["analysis_results", "discrepancy_details", "severity_assessment"],
                priority=2,
                description="Generate queries based on analysis findings"
            ),
            
            # Query Generator to Query Tracker
            HandoffRule(
                from_agent=AgentRole.QUERY_GENERATOR,
                to_agent=AgentRole.QUERY_TRACKER,
                condition="when generated queries need lifecycle tracking",
                context_transfer=["generated_queries", "site_information", "priority_levels"],
                priority=3,
                description="Track generated queries through their lifecycle"
            ),
            
            # Data Verifier to Query Generator
            HandoffRule(
                from_agent=AgentRole.DATA_VERIFIER,
                to_agent=AgentRole.QUERY_GENERATOR,
                condition="when verification discrepancies require query generation",
                context_transfer=["verification_results", "discrepancies", "critical_findings"],
                priority=2,
                description="Generate queries for verification discrepancies"
            ),
            
            # Query Tracker back to Portfolio Manager
            HandoffRule(
                from_agent=AgentRole.QUERY_TRACKER,
                to_agent=AgentRole.PORTFOLIO_MANAGER,
                condition="when tracking is complete or escalation needed",
                context_transfer=["tracking_results", "completion_status", "escalation_alerts"],
                priority=4,
                description="Report tracking completion or escalations to portfolio manager"
            ),
            
            # Query Analyzer to Data Verifier
            HandoffRule(
                from_agent=AgentRole.QUERY_ANALYZER,
                to_agent=AgentRole.DATA_VERIFIER,
                condition="when analysis identifies need for detailed verification",
                context_transfer=["analysis_results", "suspicious_data_points", "verification_targets"],
                priority=2,
                description="Verify specific data points identified during analysis"
            ),
            
            # Data Verifier back to Portfolio Manager
            HandoffRule(
                from_agent=AgentRole.DATA_VERIFIER,
                to_agent=AgentRole.PORTFOLIO_MANAGER,
                condition="when verification is complete or critical issues found",
                context_transfer=["verification_results", "critical_findings", "recommendations"],
                priority=4,
                description="Report verification results to portfolio manager"
            )
        ]
    
    def _create_sdk_handoffs(self) -> Dict[str, Handoff]:
        """Create OpenAI SDK Handoff objects from rules."""
        
        handoffs = {}
        
        for rule in self.handoff_rules:
            handoff_key = f"{rule.from_agent.value}_to_{rule.to_agent.value}"
            
            # Get target agent
            target_agent = self.agents[rule.to_agent].agent
            
            # Create SDK handoff
            handoff = Handoff(
                target_agent=target_agent,
                name=f"Handoff to {rule.to_agent.value}",
                condition=rule.condition,
                context_transfer=rule.context_transfer
            )
            
            handoffs[handoff_key] = handoff
        
        return handoffs
    
    def _register_handoffs(self) -> None:
        """Register handoffs with the appropriate agents."""
        
        # Portfolio Manager handoffs
        pm_handoffs = [
            self.sdk_handoffs["portfolio_manager_to_query_analyzer"],
            self.sdk_handoffs["portfolio_manager_to_data_verifier"]
        ]
        
        # Query Analyzer handoffs
        qa_handoffs = [
            self.sdk_handoffs["query_analyzer_to_query_generator"],
            self.sdk_handoffs["query_analyzer_to_data_verifier"]
        ]
        
        # Query Generator handoffs
        qg_handoffs = [
            self.sdk_handoffs["query_generator_to_query_tracker"]
        ]
        
        # Data Verifier handoffs
        dv_handoffs = [
            self.sdk_handoffs["data_verifier_to_query_generator"],
            self.sdk_handoffs["data_verifier_to_portfolio_manager"]
        ]
        
        # Query Tracker handoffs
        qt_handoffs = [
            self.sdk_handoffs["query_tracker_to_portfolio_manager"]
        ]
        
        # Update agent handoffs (if SDK supports this pattern)
        # Note: This depends on how the OpenAI Agents SDK implements handoff registration
        # For now, we store them in the registry for manual orchestration
        
        self.agent_handoffs = {
            AgentRole.PORTFOLIO_MANAGER: pm_handoffs,
            AgentRole.QUERY_ANALYZER: qa_handoffs,
            AgentRole.QUERY_GENERATOR: qg_handoffs,
            AgentRole.DATA_VERIFIER: dv_handoffs,
            AgentRole.QUERY_TRACKER: qt_handoffs
        }
    
    def get_available_handoffs(self, from_agent: AgentRole) -> List[Handoff]:
        """Get available handoffs for a specific agent."""
        return self.agent_handoffs.get(from_agent, [])
    
    def get_handoff_by_agents(self, from_agent: AgentRole, to_agent: AgentRole) -> Optional[Handoff]:
        """Get specific handoff between two agents."""
        handoff_key = f"{from_agent.value}_to_{to_agent.value}"
        return self.sdk_handoffs.get(handoff_key)
    
    def should_handoff(self, from_agent: AgentRole, context: Dict[str, Any]) -> List[AgentRole]:
        """Determine which agents should receive handoffs based on context."""
        
        recommended_handoffs = []
        
        # Portfolio Manager decision logic
        if from_agent == AgentRole.PORTFOLIO_MANAGER:
            if "data_analysis" in context.get("workflow_type", ""):
                recommended_handoffs.append(AgentRole.QUERY_ANALYZER)
            if "data_verification" in context.get("workflow_type", ""):
                recommended_handoffs.append(AgentRole.DATA_VERIFIER)
        
        # Query Analyzer decision logic
        elif from_agent == AgentRole.QUERY_ANALYZER:
            if context.get("discrepancies_found", 0) > 0:
                recommended_handoffs.append(AgentRole.QUERY_GENERATOR)
            if context.get("requires_verification", False):
                recommended_handoffs.append(AgentRole.DATA_VERIFIER)
        
        # Query Generator decision logic
        elif from_agent == AgentRole.QUERY_GENERATOR:
            if context.get("queries_generated", 0) > 0:
                recommended_handoffs.append(AgentRole.QUERY_TRACKER)
        
        # Data Verifier decision logic
        elif from_agent == AgentRole.DATA_VERIFIER:
            if context.get("discrepancies_found", 0) > 0:
                recommended_handoffs.append(AgentRole.QUERY_GENERATOR)
            # Always report back to Portfolio Manager
            recommended_handoffs.append(AgentRole.PORTFOLIO_MANAGER)
        
        # Query Tracker decision logic
        elif from_agent == AgentRole.QUERY_TRACKER:
            if context.get("tracking_complete", False) or context.get("escalation_needed", False):
                recommended_handoffs.append(AgentRole.PORTFOLIO_MANAGER)
        
        return recommended_handoffs
    
    async def execute_handoff(
        self, 
        from_agent: AgentRole, 
        to_agent: AgentRole, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a handoff between agents."""
        
        handoff = self.get_handoff_by_agents(from_agent, to_agent)
        if not handoff:
            return {
                "success": False,
                "error": f"No handoff defined from {from_agent.value} to {to_agent.value}"
            }
        
        try:
            # Get source and target agents
            source_agent_instance = self.agents[from_agent]
            target_agent_instance = self.agents[to_agent]
            
            # Transfer context data
            transferred_context = {}
            for field in handoff.context_transfer:
                if field in context:
                    transferred_context[field] = context[field]
            
            # Log handoff
            handoff_result = {
                "success": True,
                "from_agent": from_agent.value,
                "to_agent": to_agent.value,
                "handoff_time": context.get("timestamp", ""),
                "context_transferred": transferred_context,
                "condition_met": handoff.condition
            }
            
            # Update target agent context if possible
            if hasattr(target_agent_instance, 'context'):
                # Merge transferred context
                for key, value in transferred_context.items():
                    if hasattr(target_agent_instance.context, key):
                        setattr(target_agent_instance.context, key, value)
            
            return handoff_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "from_agent": from_agent.value,
                "to_agent": to_agent.value
            }
    
    def get_workflow_sequence(self, workflow_type: str) -> List[AgentRole]:
        """Get the typical agent sequence for a workflow type."""
        
        workflow_sequences = {
            "query_resolution": [
                AgentRole.PORTFOLIO_MANAGER,
                AgentRole.QUERY_ANALYZER,
                AgentRole.QUERY_GENERATOR,
                AgentRole.QUERY_TRACKER
            ],
            "data_verification": [
                AgentRole.PORTFOLIO_MANAGER,
                AgentRole.DATA_VERIFIER,
                AgentRole.QUERY_GENERATOR,
                AgentRole.QUERY_TRACKER
            ],
            "comprehensive_analysis": [
                AgentRole.PORTFOLIO_MANAGER,
                AgentRole.QUERY_ANALYZER,
                AgentRole.DATA_VERIFIER,
                AgentRole.QUERY_GENERATOR,
                AgentRole.QUERY_TRACKER
            ]
        }
        
        return workflow_sequences.get(workflow_type, [AgentRole.PORTFOLIO_MANAGER])
    
    def validate_handoff_sequence(self, sequence: List[AgentRole]) -> Dict[str, Any]:
        """Validate that a sequence of agent handoffs is valid."""
        
        validation_result = {
            "valid": True,
            "issues": [],
            "recommendations": []
        }
        
        for i in range(len(sequence) - 1):
            from_agent = sequence[i]
            to_agent = sequence[i + 1]
            
            handoff = self.get_handoff_by_agents(from_agent, to_agent)
            if not handoff:
                validation_result["valid"] = False
                validation_result["issues"].append(
                    f"No handoff defined from {from_agent.value} to {to_agent.value}"
                )
        
        if not validation_result["valid"]:
            validation_result["recommendations"].append(
                "Review handoff rules and define missing transitions"
            )
        
        return validation_result
    
    def get_agent_capabilities(self, agent_role: AgentRole) -> Dict[str, Any]:
        """Get capabilities of a specific agent."""
        
        capabilities = {
            AgentRole.PORTFOLIO_MANAGER: {
                "primary_function": "Workflow orchestration and coordination",
                "capabilities": [
                    "Multi-agent coordination",
                    "Workflow planning",
                    "Progress tracking",
                    "Resource allocation"
                ],
                "input_types": ["workflow_requests", "coordination_tasks"],
                "output_types": ["workflow_plans", "status_updates"]
            },
            AgentRole.QUERY_ANALYZER: {
                "primary_function": "Clinical data analysis and query identification",
                "capabilities": [
                    "Data discrepancy detection",
                    "Pattern analysis",
                    "Regulatory compliance checking",
                    "Medical terminology processing"
                ],
                "input_types": ["clinical_data", "edc_data", "analysis_requests"],
                "output_types": ["analysis_reports", "discrepancy_lists", "recommendations"]
            },
            AgentRole.QUERY_GENERATOR: {
                "primary_function": "Clinical query generation and formatting",
                "capabilities": [
                    "Medical query generation",
                    "Template-based formatting",
                    "Multi-language support",
                    "Regulatory compliance validation"
                ],
                "input_types": ["analysis_results", "discrepancy_data"],
                "output_types": ["clinical_queries", "formatted_messages"]
            },
            AgentRole.QUERY_TRACKER: {
                "primary_function": "Query lifecycle tracking and monitoring",
                "capabilities": [
                    "Status tracking",
                    "SLA monitoring",
                    "Automated follow-ups",
                    "Escalation management"
                ],
                "input_types": ["query_data", "tracking_requests"],
                "output_types": ["status_updates", "escalation_alerts", "metrics"]
            },
            AgentRole.DATA_VERIFIER: {
                "primary_function": "Cross-system data verification and validation",
                "capabilities": [
                    "Cross-system data comparison",
                    "Source data verification",
                    "Discrepancy pattern detection",
                    "Audit trail generation"
                ],
                "input_types": ["edc_data", "source_documents", "verification_requests"],
                "output_types": ["verification_reports", "discrepancy_lists", "audit_trails"]
            }
        }
        
        return capabilities.get(agent_role, {})
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get statistics about the handoff registry."""
        
        return {
            "total_agents": len(self.agents),
            "total_handoff_rules": len(self.handoff_rules),
            "agent_roles": [role.value for role in self.agents.keys()],
            "handoff_matrix": {
                rule.from_agent.value: rule.to_agent.value 
                for rule in self.handoff_rules
            },
            "workflow_types_supported": [
                "query_resolution",
                "data_verification", 
                "comprehensive_analysis"
            ]
        }


# Global registry instance
clinical_trials_registry = ClinicalTrialsHandoffRegistry()


# Convenience functions for accessing the registry
def get_agent(role: AgentRole):
    """Get an agent instance by role."""
    return clinical_trials_registry.agents.get(role)


def get_portfolio_manager() -> PortfolioManager:
    """Get the Portfolio Manager instance."""
    return clinical_trials_registry.agents[AgentRole.PORTFOLIO_MANAGER]


def get_query_analyzer() -> QueryAnalyzer:
    """Get the Query Analyzer instance."""
    return clinical_trials_registry.agents[AgentRole.QUERY_ANALYZER]


def get_query_generator() -> QueryGenerator:
    """Get the Query Generator instance."""
    return clinical_trials_registry.agents[AgentRole.QUERY_GENERATOR]


def get_query_tracker() -> QueryTracker:
    """Get the Query Tracker instance."""
    return clinical_trials_registry.agents[AgentRole.QUERY_TRACKER]


def get_data_verifier() -> DataVerifier:
    """Get the Data Verifier instance."""
    return clinical_trials_registry.agents[AgentRole.DATA_VERIFIER]


async def execute_workflow(workflow_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a complete workflow using the handoff registry."""
    
    portfolio_manager = get_portfolio_manager()
    
    # Create workflow request
    workflow_request = {
        "workflow_type": workflow_type,
        "input_data": input_data,
        "registry": clinical_trials_registry
    }
    
    # Execute workflow through Portfolio Manager
    result = await portfolio_manager.orchestrate_workflow(workflow_request)
    
    return result


__all__ = [
    "ClinicalTrialsHandoffRegistry",
    "AgentRole",
    "HandoffRule",
    "clinical_trials_registry",
    "get_agent",
    "get_portfolio_manager",
    "get_query_analyzer", 
    "get_query_generator",
    "get_query_tracker",
    "get_data_verifier",
    "execute_workflow"
]