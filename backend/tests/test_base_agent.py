"""Tests for base agent functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any, Optional
import asyncio

from app.agents.base_agent import BaseAgent, AgentResponse, AgentMessage
from app.core.config import get_settings


class TestAgentMessage:
    """Test cases for AgentMessage data class."""

    def test_agent_message_creation(self):
        """Test that AgentMessage can be created with required fields."""
        message = AgentMessage(
            role="user",
            content="Test message",
            agent_id="test-agent"
        )
        
        assert message.role == "user"
        assert message.content == "Test message"
        assert message.agent_id == "test-agent"
        assert message.timestamp is not None
        assert message.metadata == {}

    def test_agent_message_with_metadata(self):
        """Test AgentMessage with optional metadata."""
        metadata = {"confidence": 0.95, "source": "nlp"}
        message = AgentMessage(
            role="assistant",
            content="Analysis complete",
            agent_id="analyzer",
            metadata=metadata
        )
        
        assert message.metadata == metadata
        assert message.metadata["confidence"] == 0.95

    def test_agent_message_serialization(self):
        """Test that AgentMessage can be serialized to dict."""
        message = AgentMessage(
            role="system",
            content="System prompt",
            agent_id="system"
        )
        
        message_dict = message.to_dict()
        assert isinstance(message_dict, dict)
        assert message_dict["role"] == "system"
        assert message_dict["content"] == "System prompt"
        assert "timestamp" in message_dict


class TestAgentResponse:
    """Test cases for AgentResponse data class."""

    def test_agent_response_success(self):
        """Test successful AgentResponse creation."""
        response = AgentResponse(
            success=True,
            content="Task completed successfully",
            agent_id="test-agent",
            execution_time=1.5
        )
        
        assert response.success is True
        assert response.content == "Task completed successfully"
        assert response.agent_id == "test-agent"
        assert response.execution_time == 1.5
        assert response.error is None
        assert response.metadata == {}

    def test_agent_response_failure(self):
        """Test failed AgentResponse creation."""
        response = AgentResponse(
            success=False,
            content="",
            agent_id="test-agent",
            execution_time=0.5,
            error="API rate limit exceeded"
        )
        
        assert response.success is False
        assert response.error == "API rate limit exceeded"

    def test_agent_response_with_metadata(self):
        """Test AgentResponse with metadata."""
        metadata = {"tokens_used": 150, "model": "gpt-4"}
        response = AgentResponse(
            success=True,
            content="Response content",
            agent_id="test-agent",
            execution_time=2.1,
            metadata=metadata
        )
        
        assert response.metadata == metadata
        assert response.metadata["tokens_used"] == 150


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch('app.agents.base_agent.AsyncOpenAI') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def base_agent(self, mock_openai_client):
        """Create a BaseAgent instance for testing."""
        return BaseAgent(
            agent_id="test-agent",
            name="Test Agent",
            description="A test agent for unit testing",
            model="gpt-4"
        )

    def test_base_agent_initialization(self, base_agent):
        """Test BaseAgent initialization."""
        assert base_agent.agent_id == "test-agent"
        assert base_agent.name == "Test Agent"
        assert base_agent.description == "A test agent for unit testing"
        assert base_agent.model == "gpt-4"
        assert base_agent.temperature == 0.1  # Default value
        assert base_agent.max_tokens == 1000  # Default value
        assert base_agent.is_active is True
        assert base_agent.message_history == []

    def test_base_agent_with_custom_parameters(self, mock_openai_client):
        """Test BaseAgent with custom parameters."""
        agent = BaseAgent(
            agent_id="custom-agent",
            name="Custom Agent",
            description="Custom description",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=2000,
            system_prompt="You are a custom assistant."
        )
        
        assert agent.temperature == 0.7
        assert agent.max_tokens == 2000
        assert agent.system_prompt == "You are a custom assistant."

    def test_add_message(self, base_agent):
        """Test adding messages to agent history."""
        message = AgentMessage(
            role="user",
            content="Hello agent",
            agent_id="test-user"
        )
        
        base_agent.add_message(message)
        
        assert len(base_agent.message_history) == 1
        assert base_agent.message_history[0] == message

    def test_clear_history(self, base_agent):
        """Test clearing message history."""
        # Add some messages
        for i in range(3):
            message = AgentMessage(
                role="user",
                content=f"Message {i}",
                agent_id="test-user"
            )
            base_agent.add_message(message)
        
        assert len(base_agent.message_history) == 3
        
        base_agent.clear_history()
        
        assert len(base_agent.message_history) == 0

    def test_get_recent_messages(self, base_agent):
        """Test getting recent messages from history."""
        # Add multiple messages
        for i in range(5):
            message = AgentMessage(
                role="user",
                content=f"Message {i}",
                agent_id="test-user"
            )
            base_agent.add_message(message)
        
        recent = base_agent.get_recent_messages(3)
        
        assert len(recent) == 3
        assert recent[0].content == "Message 2"  # Should be chronological
        assert recent[-1].content == "Message 4"

    @pytest.mark.asyncio
    async def test_process_message_success(self, base_agent, mock_openai_client):
        """Test successful message processing."""
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Hello! How can I help you?"
        mock_completion.usage.total_tokens = 25
        
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        response = await base_agent.process_message("Hello agent")
        
        assert response.success is True
        assert response.content == "Hello! How can I help you?"
        assert response.agent_id == "test-agent"
        assert "tokens_used" in response.metadata
        assert response.metadata["tokens_used"] == 25

    @pytest.mark.asyncio
    async def test_process_message_failure(self, base_agent, mock_openai_client):
        """Test message processing with API failure."""
        # Mock OpenAI API exception
        mock_openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        response = await base_agent.process_message("Hello agent")
        
        assert response.success is False
        assert response.error == "API Error"
        assert response.agent_id == "test-agent"

    @pytest.mark.asyncio
    async def test_process_message_with_history(self, base_agent, mock_openai_client):
        """Test message processing includes conversation history."""
        # Add some history
        base_agent.add_message(AgentMessage(
            role="user",
            content="Previous question",
            agent_id="user"
        ))
        base_agent.add_message(AgentMessage(
            role="assistant",
            content="Previous answer",
            agent_id="test-agent"
        ))
        
        # Mock OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Response with context"
        mock_completion.usage.total_tokens = 50
        
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        response = await base_agent.process_message("Follow up question")
        
        # Verify the API was called with history
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        # Should include system prompt, history, and new message
        assert len(messages) >= 3
        assert messages[-1]['content'] == "Follow up question"

    def test_activate_deactivate(self, base_agent):
        """Test agent activation and deactivation."""
        assert base_agent.is_active is True
        
        base_agent.deactivate()
        assert base_agent.is_active is False
        
        base_agent.activate()
        assert base_agent.is_active is True

    @pytest.mark.asyncio
    async def test_process_message_when_inactive(self, base_agent):
        """Test that inactive agent returns error response."""
        base_agent.deactivate()
        
        response = await base_agent.process_message("Test message")
        
        assert response.success is False
        assert "Agent is not active" in response.error

    def test_build_messages_for_api(self, base_agent):
        """Test building messages for OpenAI API format."""
        # Add system prompt
        base_agent.system_prompt = "You are a helpful assistant."
        
        # Add some history
        base_agent.add_message(AgentMessage(
            role="user",
            content="First question",
            agent_id="user"
        ))
        base_agent.add_message(AgentMessage(
            role="assistant",
            content="First answer",
            agent_id="test-agent"
        ))
        
        messages = base_agent._build_messages_for_api("New question")
        
        assert len(messages) == 4  # system + 2 history + new
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == "You are a helpful assistant."
        assert messages[-1]['role'] == 'user'
        assert messages[-1]['content'] == "New question"

    def test_agent_statistics(self, base_agent):
        """Test agent statistics tracking."""
        stats = base_agent.get_stats()
        
        assert 'message_count' in stats
        assert 'total_execution_time' in stats
        assert 'average_execution_time' in stats
        assert 'success_rate' in stats
        
        assert stats['message_count'] == 0
        assert stats['total_execution_time'] == 0
        assert stats['success_rate'] == 0

    @pytest.mark.asyncio
    async def test_agent_statistics_after_processing(self, base_agent, mock_openai_client):
        """Test agent statistics after processing messages."""
        # Mock successful response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Response"
        mock_completion.usage.total_tokens = 20
        
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        # Process a message
        await base_agent.process_message("Test message")
        
        stats = base_agent.get_stats()
        assert stats['message_count'] == 1
        assert stats['success_rate'] == 100.0
        assert stats['total_execution_time'] > 0


class TestAgentConfigurationValidation:
    """Test agent configuration validation."""

    @patch('app.agents.base_agent.AsyncOpenAI')
    def test_invalid_agent_id(self, mock_openai_class):
        """Test that invalid agent IDs raise errors."""
        with pytest.raises(ValueError, match="Agent ID cannot be empty"):
            BaseAgent(
                agent_id="",
                name="Test Agent",
                description="Test description"
            )

    @patch('app.agents.base_agent.AsyncOpenAI')
    def test_invalid_temperature(self, mock_openai_class):
        """Test that invalid temperature values raise errors."""
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            BaseAgent(
                agent_id="test-agent",
                name="Test Agent",
                description="Test description",
                temperature=3.0
            )

    @patch('app.agents.base_agent.AsyncOpenAI')
    def test_invalid_max_tokens(self, mock_openai_class):
        """Test that invalid max_tokens values raise errors."""
        with pytest.raises(ValueError, match="Max tokens must be positive"):
            BaseAgent(
                agent_id="test-agent",
                name="Test Agent",
                description="Test description",
                max_tokens=-100
            )


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()