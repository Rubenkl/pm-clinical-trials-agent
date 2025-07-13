"""
Dashboard metrics endpoints for clinical trials management.
Provides comprehensive overview and real-time metrics for the platform.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app.api.models.structured_responses import (
    AgentActivity,
    DashboardOverviewResponse,
    QueryStatistics,
    SDVStatistics,
    SystemHealthMetrics,
    TrialOverviewResponse,
)
from app.services.monitoring_service import get_monitoring_service

router = APIRouter()


async def get_mock_trial_metrics() -> TrialOverviewResponse:
    """Generate mock trial overview metrics"""
    return TrialOverviewResponse(
        trial_id="CARD-2025-001",
        trial_name="Cardiovascular Outcomes Phase 2 Study",
        phase="II",
        # Enrollment metrics
        enrolled_subjects=50,
        target_enrollment=120,
        enrollment_percentage=41.7,
        enrollment_trend="on_track",
        # Query metrics
        open_queries=23,
        query_rate_change=-12.5,  # 12.5% decrease from last period
        average_query_age=3.2,
        # SDV metrics
        sdv_completion=78.5,
        sdv_findings=156,
        # Deviation metrics
        major_deviations=3,
        minor_deviations=12,
        deviation_rate=0.3,  # per subject
        # Site performance
        total_sites=3,
        active_sites=3,
        sites_at_risk=1,
        # Overall health score
        health_score=82.5,
        health_trend="stable",
        # Key risks
        key_risks=[
            {
                "risk_type": "enrollment",
                "description": "Site 3 enrollment behind target",
                "severity": "medium",
                "impact": "Schedule risk",
                "mitigation": "Additional recruitment activities planned",
            },
            {
                "risk_type": "data_quality",
                "description": "Higher than expected query rate at Site 2",
                "severity": "low",
                "impact": "Data quality concerns",
                "mitigation": "Additional training scheduled",
            },
        ],
        # Recent agent insights
        agent_insights=[
            "Hemoglobin values show concerning trend in 8% of subjects",
            "Blood pressure monitoring compliance at 95%",
            "Query resolution time improved by 15% this month",
            "SDV completion ahead of schedule at Sites 1 and 2",
        ],
    )


async def get_mock_query_statistics() -> QueryStatistics:
    """Generate mock query statistics"""
    return QueryStatistics(
        total_queries=234,
        open_queries=45,
        critical_queries=5,
        major_queries=23,
        minor_queries=17,
        resolved_today=12,
        resolved_this_week=78,
        average_resolution_time=24.5,
        queries_by_site={"SITE01": 15, "SITE02": 18, "SITE03": 12},
        queries_by_category={
            "laboratory_value": 20,
            "vital_signs": 15,
            "adverse_event": 8,
            "concomitant_medication": 2,
        },
        trend_data=[
            {"date": "2025-01-05", "queries": 8},
            {"date": "2025-01-06", "queries": 12},
            {"date": "2025-01-07", "queries": 15},
            {"date": "2025-01-08", "queries": 10},
            {"date": "2025-01-09", "queries": 6},
        ],
    )


async def get_mock_sdv_statistics() -> SDVStatistics:
    """Generate mock SDV statistics"""
    return SDVStatistics(
        total_subjects=50,
        verified_subjects=39,
        total_data_points=2400,
        verified_data_points=1884,
        overall_completion=78.5,
        discrepancy_rate=0.045,  # 4.5%
        sites_summary=[
            {
                "site_id": "SITE01",
                "site_name": "Boston General Hospital",
                "completion_rate": 85.2,
                "discrepancy_rate": 0.032,
                "subjects_verified": 15,
                "total_subjects": 18,
            },
            {
                "site_id": "SITE02",
                "site_name": "Cleveland Clinic",
                "completion_rate": 82.7,
                "discrepancy_rate": 0.041,
                "subjects_verified": 14,
                "total_subjects": 17,
            },
            {
                "site_id": "SITE03",
                "site_name": "Mayo Clinic",
                "completion_rate": 66.7,
                "discrepancy_rate": 0.068,
                "subjects_verified": 10,
                "total_subjects": 15,
            },
        ],
        high_risk_sites=["SITE03"],
        resource_utilization={
            "total_monitor_hours": 156.5,
            "hours_per_subject": 3.9,
            "efficiency_score": 0.78,
        },
    )


async def get_mock_system_health() -> SystemHealthMetrics:
    """Generate mock system health metrics"""
    return SystemHealthMetrics(
        agents_online=5,
        total_agents=5,
        average_response_time=1.8,
        queries_processed_today=27,
        sdv_completed_today=8,
        deviations_detected_today=2,
        system_uptime=99.7,
        active_workflows=12,
        error_rate=0.003,
        agent_activities=[
            AgentActivity(
                timestamp=datetime.now() - timedelta(minutes=5),
                agent_id="portfolio-manager",
                agent_name="Portfolio Manager",
                action="workflow_orchestrated",
                details="Completed comprehensive analysis for CARD001",
                impact="Query generated",
                execution_time=4.2,
            ),
            AgentActivity(
                timestamp=datetime.now() - timedelta(minutes=12),
                agent_id="query-analyzer",
                agent_name="Query Analyzer",
                action="clinical_analysis",
                details="Analyzed hemoglobin values for 3 subjects",
                impact="2 discrepancies identified",
                execution_time=2.1,
            ),
            AgentActivity(
                timestamp=datetime.now() - timedelta(minutes=18),
                agent_id="data-verifier",
                agent_name="Data Verifier",
                action="sdv_verification",
                details="Verified 15 data points for CARD005",
                impact="3 discrepancies found",
                execution_time=3.8,
            ),
        ],
    )


@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview():
    """Get comprehensive dashboard overview with all key metrics"""
    try:
        # Get all metric components
        trial_metrics = await get_mock_trial_metrics()
        query_statistics = await get_mock_query_statistics()
        sdv_statistics = await get_mock_sdv_statistics()
        system_health = await get_mock_system_health()

        # Generate critical alerts
        critical_alerts = []
        if query_statistics.critical_queries > 0:
            critical_alerts.append(
                {
                    "alert_id": "CRIT_001",
                    "type": "critical_queries",
                    "message": f"{query_statistics.critical_queries} critical queries require immediate attention",
                    "severity": "high",
                    "created_at": datetime.now().isoformat(),
                }
            )

        if trial_metrics.sites_at_risk > 0:
            critical_alerts.append(
                {
                    "alert_id": "CRIT_002",
                    "type": "site_performance",
                    "message": f"{trial_metrics.sites_at_risk} site(s) require attention",
                    "severity": "medium",
                    "created_at": datetime.now().isoformat(),
                }
            )

        # Generate pending actions
        pending_actions = [
            {
                "action_id": "ACT_001",
                "type": "query_review",
                "description": "Review 5 critical queries from last 24 hours",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(hours=4)).isoformat(),
                "assigned_to": "medical_monitor",
            },
            {
                "action_id": "ACT_002",
                "type": "sdv_review",
                "description": "Complete SDV for 11 pending subjects",
                "priority": "medium",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "assigned_to": "data_manager",
            },
        ]

        # Performance summary
        performance_summary = {
            "overall_score": 82.5,
            "query_performance": {
                "resolution_time": query_statistics.average_resolution_time,
                "resolution_rate": 89.2,
                "trend": "improving",
            },
            "sdv_performance": {
                "completion_rate": sdv_statistics.overall_completion,
                "quality_score": 94.8,
                "trend": "stable",
            },
            "system_performance": {
                "uptime": system_health.system_uptime,
                "response_time": system_health.average_response_time,
                "trend": "stable",
            },
        }

        return DashboardOverviewResponse(
            trial_metrics=trial_metrics,
            query_statistics=query_statistics,
            sdv_statistics=sdv_statistics,
            system_health=system_health,
            recent_activities=system_health.agent_activities,
            critical_alerts=critical_alerts,
            pending_actions=pending_actions,
            performance_summary=performance_summary,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve dashboard overview: {str(e)}"
        )


@router.get("/metrics/queries", response_model=QueryStatistics)
async def get_query_metrics():
    """Get detailed query metrics"""
    try:
        return await get_mock_query_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve query metrics: {str(e)}"
        )


@router.get("/metrics/sdv", response_model=SDVStatistics)
async def get_sdv_metrics():
    """Get detailed SDV metrics"""
    try:
        return await get_mock_sdv_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve SDV metrics: {str(e)}"
        )


@router.get("/metrics/system", response_model=SystemHealthMetrics)
async def get_system_metrics():
    """Get system health and performance metrics"""
    try:
        return await get_mock_system_health()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve system metrics: {str(e)}"
        )


@router.get("/metrics/trial", response_model=TrialOverviewResponse)
async def get_trial_metrics():
    """Get trial overview metrics"""
    try:
        return await get_mock_trial_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve trial metrics: {str(e)}"
        )


# Real-time metrics endpoints for dashboard updates


@router.get("/realtime/alerts")
async def get_realtime_alerts():
    """Get real-time alerts and notifications"""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "alerts": [
                {
                    "id": "ALERT_001",
                    "type": "critical_query",
                    "message": "New critical query generated for CARD015",
                    "severity": "high",
                    "created_at": datetime.now().isoformat(),
                }
            ],
            "notifications": [
                {
                    "id": "NOTIF_001",
                    "type": "workflow_completed",
                    "message": "SDV workflow completed for 5 subjects",
                    "created_at": datetime.now().isoformat(),
                }
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve real-time alerts: {str(e)}"
        )


@router.get("/realtime/activity")
async def get_realtime_activity():
    """Get real-time agent activity feed"""
    try:
        return {
            "timestamp": datetime.now().isoformat(),
            "activities": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "agent": "Query Analyzer",
                    "action": "Clinical data analysis completed",
                    "details": "Analyzed BP and hemoglobin values for CARD022",
                    "impact": "1 query generated",
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=3)).isoformat(),
                    "agent": "Data Verifier",
                    "action": "SDV verification in progress",
                    "details": "Verifying laboratory results for CARD018",
                    "impact": "15/20 data points verified",
                },
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve real-time activity: {str(e)}"
        )


# Monitoring service endpoints


@router.get("/monitoring/status")
async def get_monitoring_status():
    """Get monitoring service status and statistics"""
    try:
        monitoring_service = get_monitoring_service()
        return monitoring_service.get_monitoring_status()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve monitoring status: {str(e)}"
        )


@router.get("/monitoring/alerts")
async def get_monitoring_alerts():
    """Get active monitoring alerts"""
    try:
        monitoring_service = get_monitoring_service()
        return {
            "alerts": monitoring_service.get_active_alerts(),
            "total_alerts": len(monitoring_service.get_active_alerts()),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve monitoring alerts: {str(e)}"
        )


@router.post("/monitoring/start")
async def start_monitoring():
    """Start background monitoring service"""
    try:
        monitoring_service = get_monitoring_service()
        await monitoring_service.start_monitoring()
        return {
            "success": True,
            "message": "Monitoring service started successfully",
            "status": monitoring_service.get_monitoring_status(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start monitoring service: {str(e)}"
        )


@router.post("/monitoring/stop")
async def stop_monitoring():
    """Stop background monitoring service"""
    try:
        monitoring_service = get_monitoring_service()
        await monitoring_service.stop_monitoring()
        return {
            "success": True,
            "message": "Monitoring service stopped successfully",
            "status": monitoring_service.get_monitoring_status(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to stop monitoring service: {str(e)}"
        )


@router.delete("/monitoring/alerts")
async def clear_monitoring_alerts(alert_ids: Optional[List[str]] = None):
    """Clear monitoring alerts"""
    try:
        monitoring_service = get_monitoring_service()
        monitoring_service.clear_alerts(alert_ids)
        return {
            "success": True,
            "message": "Alerts cleared successfully",
            "remaining_alerts": len(monitoring_service.get_active_alerts()),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear monitoring alerts: {str(e)}"
        )
