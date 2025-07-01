"""Tests for Query Tracker Agent using OpenAI Agents SDK."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

from app.agents.query_tracker import QueryTracker, QueryStatus, TrackedQuery


class TestQueryTracker:
    """Test suite for Query Tracker agent."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('app.agents.query_tracker.OpenAI') as mock_client:
            # Mock assistant
            mock_assistant = Mock()
            mock_assistant.id = "asst_tracker123"
            mock_assistant.name = "Clinical Query Tracker"
            
            # Mock thread
            mock_thread = Mock()
            mock_thread.id = "thread_tracker123"
            
            # Mock message for tracking response
            mock_message = Mock()
            mock_message.content = [Mock(text=Mock(value=json.dumps({
                "status": "pending",
                "follow_up_needed": True,
                "follow_up_message": "Gentle reminder about pending query",
                "escalation_level": 1,
                "next_action": "send_reminder",
                "sla_status": "on_track"
            })))]
            
            # Mock run
            mock_run = Mock()
            mock_run.status = "completed"
            mock_run.id = "run_tracker123"
            
            # Set up client methods
            mock_client.return_value.beta.assistants.create.return_value = mock_assistant
            mock_client.return_value.beta.threads.create.return_value = mock_thread
            mock_client.return_value.beta.threads.messages.create.return_value = Mock()
            mock_client.return_value.beta.threads.runs.create.return_value = mock_run
            mock_client.return_value.beta.threads.runs.retrieve.return_value = mock_run
            mock_client.return_value.beta.threads.messages.list.return_value = Mock(data=[mock_message])
            
            yield mock_client
    
    @pytest.fixture
    def query_tracker(self, mock_openai_client):
        """Create QueryTracker instance with mocked client."""
        return QueryTracker()
    
    @pytest.fixture
    def sample_query(self) -> Dict[str, Any]:
        """Sample query data for testing."""
        return {
            "query_id": "QRY_SUBJ001_20250129143022",
            "query_text": "Please verify hemoglobin value",
            "category": "data_discrepancy",
            "priority": "major",
            "subject_id": "SUBJ001",
            "site_id": "SITE001",
            "created_at": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "sla_hours": 120  # 5 business days
        }
    
    def test_query_tracker_initialization(self, query_tracker):
        """Test QueryTracker initialization."""
        assert query_tracker.assistant is not None
        assert query_tracker.instructions is not None
        assert query_tracker.escalation_rules is not None
        assert len(query_tracker.escalation_rules) >= 3
        assert query_tracker.tracked_queries == {}
    
    def test_escalation_rules_initialization(self, query_tracker):
        """Test escalation rules are properly set up."""
        rules = query_tracker.escalation_rules
        assert "critical" in rules
        assert "major" in rules
        assert "minor" in rules
        
        # Check critical escalation timing
        assert rules["critical"]["levels"][0]["after_hours"] == 24
        assert rules["critical"]["levels"][1]["after_hours"] == 48
    
    @pytest.mark.asyncio
    async def test_track_query_basic(self, query_tracker, sample_query):
        """Test basic query tracking."""
        result = await query_tracker.track_query(sample_query)
        
        assert result is not None
        assert "tracking_id" in result
        assert result["query_id"] == sample_query["query_id"]
        assert result["status"] == "tracking_started"
        assert "tracked_at" in result
        
        # Check query is stored internally
        assert sample_query["query_id"] in query_tracker.tracked_queries
    
    @pytest.mark.asyncio
    async def test_update_query_status(self, query_tracker, sample_query):
        """Test updating query status."""
        # First track the query
        await query_tracker.track_query(sample_query)
        
        # Update status
        update_result = await query_tracker.update_status(
            sample_query["query_id"],
            QueryStatus.IN_PROGRESS,
            "Site has acknowledged and is working on response"
        )
        
        assert update_result["success"] is True
        assert update_result["new_status"] == QueryStatus.IN_PROGRESS.value
        assert "updated_at" in update_result
    
    @pytest.mark.asyncio
    async def test_check_follow_ups_needed(self, query_tracker, sample_query):
        """Test checking for needed follow-ups."""
        # Track multiple queries with different statuses
        queries = [
            {**sample_query, "query_id": "QRY001", "created_at": (datetime.now() - timedelta(days=3)).isoformat()},
            {**sample_query, "query_id": "QRY002", "created_at": (datetime.now() - timedelta(days=6)).isoformat()},
            {**sample_query, "query_id": "QRY003", "created_at": datetime.now().isoformat()}
        ]
        
        for query in queries:
            await query_tracker.track_query(query)
        
        # Check follow-ups
        follow_ups = await query_tracker.check_follow_ups()
        
        assert len(follow_ups) >= 1  # At least one query needs follow-up
        assert all("query_id" in f for f in follow_ups)
        assert all("action" in f for f in follow_ups)
    
    @pytest.mark.asyncio
    async def test_generate_follow_up_message(self, query_tracker, sample_query):
        """Test follow-up message generation."""
        # Track and age the query
        sample_query["created_at"] = (datetime.now() - timedelta(days=4)).isoformat()
        await query_tracker.track_query(sample_query)
        
        # Generate follow-up
        follow_up = await query_tracker.generate_follow_up(
            sample_query["query_id"],
            escalation_level=1
        )
        
        assert follow_up is not None
        assert "message" in follow_up
        assert "escalation_level" in follow_up
        assert len(follow_up["message"]) > 50
        assert follow_up["escalation_level"] == 1
    
    @pytest.mark.asyncio
    async def test_escalation_levels(self, query_tracker):
        """Test different escalation levels."""
        critical_query = {
            "query_id": "QRY_CRITICAL_001",
            "priority": "critical",
            "created_at": (datetime.now() - timedelta(hours=25)).isoformat(),
            "sla_hours": 24
        }
        
        # Check escalation needed
        escalation = await query_tracker.check_escalation(critical_query)
        
        assert escalation["needs_escalation"] is True
        assert escalation["escalation_level"] >= 1
        assert "escalate_to" in escalation
    
    @pytest.mark.asyncio
    async def test_bulk_status_update(self, query_tracker):
        """Test bulk status updates."""
        query_ids = ["QRY001", "QRY002", "QRY003"]
        
        # Track queries first
        for qid in query_ids:
            await query_tracker.track_query({
                "query_id": qid,
                "priority": "major",
                "created_at": datetime.now().isoformat()
            })
        
        # Bulk update
        result = await query_tracker.bulk_update_status(
            query_ids,
            QueryStatus.RESOLVED
        )
        
        assert result["success"] is True
        assert result["updated_count"] == 3
        assert all(q.status == QueryStatus.RESOLVED for q in query_tracker.tracked_queries.values())
    
    @pytest.mark.asyncio
    async def test_get_query_metrics(self, query_tracker):
        """Test query metrics generation."""
        # Track queries with different statuses
        queries = [
            {"query_id": "Q1", "status": QueryStatus.PENDING},
            {"query_id": "Q2", "status": QueryStatus.IN_PROGRESS},
            {"query_id": "Q3", "status": QueryStatus.RESOLVED},
            {"query_id": "Q4", "status": QueryStatus.RESOLVED},
            {"query_id": "Q5", "status": QueryStatus.CANCELLED}
        ]
        
        for query in queries:
            tracked = TrackedQuery(
                query_id=query["query_id"],
                status=query["status"],
                created_at=datetime.now(),
                priority="major"
            )
            query_tracker.tracked_queries[query["query_id"]] = tracked
        
        metrics = query_tracker.get_metrics()
        
        assert metrics["total_queries"] == 5
        assert metrics["pending_queries"] == 1
        assert metrics["in_progress_queries"] == 1
        assert metrics["resolved_queries"] == 2
        assert metrics["resolution_rate"] == 0.4  # 2/5
    
    @pytest.mark.asyncio
    async def test_sla_monitoring(self, query_tracker, sample_query):
        """Test SLA monitoring and alerts."""
        # Create query approaching SLA breach
        sample_query["created_at"] = (datetime.now() - timedelta(hours=110)).isoformat()
        sample_query["sla_hours"] = 120  # 5 days
        
        await query_tracker.track_query(sample_query)
        
        # Check SLA status
        sla_status = await query_tracker.check_sla_status(sample_query["query_id"])
        
        assert sla_status["at_risk"] is True
        assert sla_status["hours_remaining"] < 12
        assert "percentage_consumed" in sla_status
        assert sla_status["percentage_consumed"] > 90
    
    @pytest.mark.asyncio
    async def test_query_history(self, query_tracker, sample_query):
        """Test query history tracking."""
        await query_tracker.track_query(sample_query)
        
        # Add some history events
        await query_tracker.add_history_event(
            sample_query["query_id"],
            "reminder_sent",
            "First reminder sent to site"
        )
        
        await query_tracker.add_history_event(
            sample_query["query_id"],
            "site_responded",
            "Site acknowledged receipt"
        )
        
        # Get history
        history = query_tracker.get_query_history(sample_query["query_id"])
        
        assert len(history) >= 3  # Initial tracking + 2 events
        assert history[0]["event_type"] == "query_tracked"
        assert history[1]["event_type"] == "reminder_sent"
        assert history[2]["event_type"] == "site_responded"
    
    def test_query_status_enum(self):
        """Test QueryStatus enum values."""
        assert QueryStatus.PENDING.value == "pending"
        assert QueryStatus.IN_PROGRESS.value == "in_progress"
        assert QueryStatus.RESOLVED.value == "resolved"
        assert QueryStatus.CANCELLED.value == "cancelled"
        assert QueryStatus.ESCALATED.value == "escalated"
    
    @pytest.mark.asyncio
    async def test_auto_close_resolved_queries(self, query_tracker):
        """Test auto-closing of resolved queries."""
        # Create resolved query older than 30 days
        old_query = TrackedQuery(
            query_id="QRY_OLD_001",
            status=QueryStatus.RESOLVED,
            created_at=datetime.now() - timedelta(days=35),
            resolved_at=datetime.now() - timedelta(days=32),
            priority="minor"
        )
        
        query_tracker.tracked_queries["QRY_OLD_001"] = old_query
        
        # Run auto-close
        closed = await query_tracker.auto_close_old_queries(days_old=30)
        
        assert closed["closed_count"] == 1
        assert "QRY_OLD_001" not in query_tracker.tracked_queries
    
    @pytest.mark.asyncio
    async def test_priority_based_follow_up(self, query_tracker):
        """Test priority-based follow-up timing."""
        queries = [
            {"query_id": "Q_CRIT", "priority": "critical", "created_at": (datetime.now() - timedelta(hours=25)).isoformat()},
            {"query_id": "Q_MAJ", "priority": "major", "created_at": (datetime.now() - timedelta(days=3)).isoformat()},
            {"query_id": "Q_MIN", "priority": "minor", "created_at": (datetime.now() - timedelta(days=6)).isoformat()}
        ]
        
        for query in queries:
            await query_tracker.track_query(query)
        
        # Check follow-ups
        follow_ups = await query_tracker.check_follow_ups()
        
        # Critical should be first priority
        critical_follow_up = next((f for f in follow_ups if f["query_id"] == "Q_CRIT"), None)
        assert critical_follow_up is not None
        assert critical_follow_up.get("priority_score", 0) > 100  # High priority score