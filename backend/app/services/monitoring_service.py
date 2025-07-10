"""
Continuous monitoring service for proactive clinical data detection.
Implements background monitoring loops for automatic discrepancy detection and alerting.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from app.api.dependencies import get_portfolio_manager

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration for monitoring service"""
    # Monitoring intervals (in seconds)
    critical_check_interval: int = 300  # 5 minutes
    routine_check_interval: int = 1800  # 30 minutes
    sdv_check_interval: int = 3600  # 1 hour
    
    # Thresholds
    critical_query_threshold: int = 5
    overdue_query_threshold: int = 24  # hours
    discrepancy_rate_threshold: float = 0.05  # 5%
    
    # Monitoring flags
    enable_critical_monitoring: bool = True
    enable_routine_monitoring: bool = True
    enable_sdv_monitoring: bool = True
    enable_deviation_monitoring: bool = True


@dataclass 
class MonitoringState:
    """State tracking for monitoring service"""
    last_critical_check: Optional[datetime] = None
    last_routine_check: Optional[datetime] = None
    last_sdv_check: Optional[datetime] = None
    
    active_alerts: List[Dict[str, Any]] = field(default_factory=list)
    monitoring_statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Performance tracking
    checks_performed: int = 0
    alerts_generated: int = 0
    workflows_triggered: int = 0


class ClinicalMonitoringService:
    """Continuous monitoring service for clinical trials"""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.state = MonitoringState()
        self.is_running = False
        self._monitoring_tasks: List[asyncio.Task] = []
        
    async def start_monitoring(self):
        """Start all monitoring loops"""
        if self.is_running:
            logger.warning("Monitoring service already running")
            return
            
        self.is_running = True
        logger.info("Starting clinical monitoring service...")
        
        # Start monitoring tasks
        if self.config.enable_critical_monitoring:
            task = asyncio.create_task(self._critical_monitoring_loop())
            self._monitoring_tasks.append(task)
            
        if self.config.enable_routine_monitoring:
            task = asyncio.create_task(self._routine_monitoring_loop())
            self._monitoring_tasks.append(task)
            
        if self.config.enable_sdv_monitoring:
            task = asyncio.create_task(self._sdv_monitoring_loop())
            self._monitoring_tasks.append(task)
            
        if self.config.enable_deviation_monitoring:
            task = asyncio.create_task(self._deviation_monitoring_loop())
            self._monitoring_tasks.append(task)
            
        logger.info(f"Started {len(self._monitoring_tasks)} monitoring loops")
        
    async def stop_monitoring(self):
        """Stop all monitoring loops"""
        if not self.is_running:
            return
            
        logger.info("Stopping clinical monitoring service...")
        self.is_running = False
        
        # Cancel all monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()
            
        # Wait for tasks to complete
        if self._monitoring_tasks:
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
            
        self._monitoring_tasks.clear()
        logger.info("Clinical monitoring service stopped")
        
    async def _critical_monitoring_loop(self):
        """Critical monitoring loop - runs every 5 minutes"""
        while self.is_running:
            try:
                await self._perform_critical_checks()
                self.state.last_critical_check = datetime.now()
                await asyncio.sleep(self.config.critical_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in critical monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
                
    async def _routine_monitoring_loop(self):
        """Routine monitoring loop - runs every 30 minutes"""
        while self.is_running:
            try:
                await self._perform_routine_checks()
                self.state.last_routine_check = datetime.now()
                await asyncio.sleep(self.config.routine_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in routine monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
                
    async def _sdv_monitoring_loop(self):
        """SDV monitoring loop - runs every hour"""
        while self.is_running:
            try:
                await self._perform_sdv_checks()
                self.state.last_sdv_check = datetime.now()
                await asyncio.sleep(self.config.sdv_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SDV monitoring loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retrying
                
    async def _deviation_monitoring_loop(self):
        """Protocol deviation monitoring loop - runs every hour"""
        while self.is_running:
            try:
                await self._perform_deviation_checks()
                await asyncio.sleep(3600)  # 1 hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in deviation monitoring loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retrying
                
    async def _perform_critical_checks(self):
        """Perform critical safety and compliance checks"""
        logger.debug("Performing critical monitoring checks...")
        self.state.checks_performed += 1
        
        try:
            portfolio_manager = get_portfolio_manager()
            
            # Check for critical queries that need immediate attention
            critical_query_request = {
                "workflow_id": f"CRIT_MONITOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "workflow_type": "critical_monitoring",
                "monitoring_type": "critical_queries",
                "thresholds": {
                    "critical_count": self.config.critical_query_threshold,
                    "overdue_hours": self.config.overdue_query_threshold
                }
            }
            
            # Trigger monitoring workflow
            result = await portfolio_manager.orchestrate_query_workflow(critical_query_request)
            
            if result.get("success") and result.get("automated_actions"):
                await self._process_monitoring_result(result, "critical")
                
            # Check for safety-critical lab values
            safety_request = {
                "workflow_id": f"SAFETY_MONITOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "workflow_type": "safety_monitoring",
                "monitoring_type": "critical_values",
                "data_points": [
                    {"field_name": "hemoglobin", "safety_threshold": 8.0},
                    {"field_name": "systolic_bp", "safety_threshold": 180},
                    {"field_name": "heart_rate", "safety_threshold": 120}
                ]
            }
            
            safety_result = await portfolio_manager.orchestrate_query_workflow(safety_request)
            if safety_result.get("success"):
                await self._process_monitoring_result(safety_result, "safety")
                
        except Exception as e:
            logger.error(f"Critical monitoring check failed: {e}")
            
    async def _perform_routine_checks(self):
        """Perform routine data quality and compliance checks"""
        logger.debug("Performing routine monitoring checks...")
        self.state.checks_performed += 1
        
        try:
            portfolio_manager = get_portfolio_manager()
            
            # Check overall data quality trends
            quality_request = {
                "workflow_id": f"QUALITY_MONITOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "workflow_type": "quality_monitoring",
                "monitoring_type": "data_quality",
                "time_window": "24_hours",
                "quality_thresholds": {
                    "discrepancy_rate": self.config.discrepancy_rate_threshold,
                    "query_rate": 0.1,  # 10% of data points
                    "completion_rate": 0.95  # 95% completion expected
                }
            }
            
            result = await portfolio_manager.orchestrate_query_workflow(quality_request)
            if result.get("success"):
                await self._process_monitoring_result(result, "routine")
                
        except Exception as e:
            logger.error(f"Routine monitoring check failed: {e}")
            
    async def _perform_sdv_checks(self):
        """Perform SDV progress and quality monitoring"""
        logger.debug("Performing SDV monitoring checks...")
        self.state.checks_performed += 1
        
        try:
            portfolio_manager = get_portfolio_manager()
            
            # Monitor SDV completion and quality
            sdv_request = {
                "study_id": "CARD-2025-001",
                "site_ids": ["SITE01", "SITE02", "SITE03"],
                "sdv_type": "routine_monitoring",
                "completion_thresholds": {
                    "minimum_completion": 0.80,  # 80% completion expected
                    "target_completion": 0.95,   # 95% target
                    "overdue_threshold": 7        # 7 days overdue
                }
            }
            
            result = await portfolio_manager.orchestrate_sdv_workflow(sdv_request)
            if result.get("success"):
                await self._process_monitoring_result(result, "sdv")
                
        except Exception as e:
            logger.error(f"SDV monitoring check failed: {e}")
            
    async def _perform_deviation_checks(self):
        """Perform protocol deviation monitoring"""
        logger.debug("Performing deviation monitoring checks...")
        self.state.checks_performed += 1
        
        try:
            portfolio_manager = get_portfolio_manager()
            
            # Monitor for new protocol deviations
            deviation_request = {
                "study_id": "CARD-2025-001",
                "monitoring_type": "proactive_deviation_detection",
                "time_window": "1_hour",
                "deviation_categories": [
                    "visit_window",
                    "prohibited_medication", 
                    "vital_signs",
                    "laboratory_value",
                    "fasting_requirement"
                ]
            }
            
            result = await portfolio_manager.orchestrate_deviation_workflow(deviation_request)
            if result.get("success"):
                await self._process_monitoring_result(result, "deviation")
                
        except Exception as e:
            logger.error(f"Deviation monitoring check failed: {e}")
            
    async def _process_monitoring_result(self, result: Dict[str, Any], check_type: str):
        """Process monitoring results and generate alerts if needed"""
        
        # Check for critical findings that need alerts
        if check_type == "critical" or check_type == "safety":
            critical_findings = result.get("critical_findings", [])
            if critical_findings:
                await self._generate_alert({
                    "alert_type": "critical_finding",
                    "check_type": check_type,
                    "findings": critical_findings,
                    "severity": "high",
                    "generated_at": datetime.now().isoformat(),
                    "workflow_id": result.get("workflow_id", "")
                })
                
        # Check for automated actions that were triggered
        automated_actions = result.get("automated_actions", [])
        if automated_actions:
            self.state.workflows_triggered += len(automated_actions)
            
        # Update monitoring statistics
        self.state.monitoring_statistics[check_type] = {
            "last_check": datetime.now().isoformat(),
            "result_summary": result.get("dashboard_update", {}),
            "execution_time": result.get("execution_time", 0),
            "success": result.get("success", False)
        }
        
    async def _generate_alert(self, alert_data: Dict[str, Any]):
        """Generate monitoring alert"""
        alert = {
            "alert_id": f"MONITOR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            **alert_data
        }
        
        self.state.active_alerts.append(alert)
        self.state.alerts_generated += 1
        
        logger.warning(f"Monitoring alert generated: {alert['alert_type']} - {alert.get('severity', 'medium')}")
        
        # Here you could add integration with external alerting systems
        # For example: send to Slack, email, SMS, etc.
        
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring service status"""
        return {
            "is_running": self.is_running,
            "active_loops": len(self._monitoring_tasks),
            "last_checks": {
                "critical": self.state.last_critical_check.isoformat() if self.state.last_critical_check else None,
                "routine": self.state.last_routine_check.isoformat() if self.state.last_routine_check else None,
                "sdv": self.state.last_sdv_check.isoformat() if self.state.last_sdv_check else None,
            },
            "statistics": {
                "checks_performed": self.state.checks_performed,
                "alerts_generated": self.state.alerts_generated,
                "workflows_triggered": self.state.workflows_triggered,
                "active_alerts": len(self.state.active_alerts)
            },
            "configuration": {
                "critical_interval": self.config.critical_check_interval,
                "routine_interval": self.config.routine_check_interval,
                "sdv_interval": self.config.sdv_check_interval,
                "monitoring_enabled": {
                    "critical": self.config.enable_critical_monitoring,
                    "routine": self.config.enable_routine_monitoring,
                    "sdv": self.config.enable_sdv_monitoring,
                    "deviation": self.config.enable_deviation_monitoring
                }
            }
        }
        
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active monitoring alerts"""
        return self.state.active_alerts.copy()
        
    def clear_alerts(self, alert_ids: Optional[List[str]] = None):
        """Clear monitoring alerts"""
        if alert_ids:
            self.state.active_alerts = [
                alert for alert in self.state.active_alerts 
                if alert["alert_id"] not in alert_ids
            ]
        else:
            self.state.active_alerts.clear()


# Global monitoring service instance
_monitoring_service: Optional[ClinicalMonitoringService] = None


def get_monitoring_service() -> ClinicalMonitoringService:
    """Get or create the global monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = ClinicalMonitoringService()
    return _monitoring_service


async def start_background_monitoring():
    """Start background monitoring service"""
    service = get_monitoring_service()
    await service.start_monitoring()
    logger.info("Background monitoring started")


async def stop_background_monitoring():
    """Stop background monitoring service"""
    service = get_monitoring_service()
    await service.stop_monitoring()
    logger.info("Background monitoring stopped")