"""
Test suite for the Multi-Provider AI Chat API

This module contains unit tests for the FastAPI application.
Run with: pytest test_app.py
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import httpx

from app import app, settings


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert "providers" in data
        assert isinstance(data["providers"], dict)
    
    def test_health_check_provider_status(self, client):
        """Test provider availability in health check."""
        response = client.get("/health")
        data = response.json()
        
        providers = data["providers"]
        assert "openai" in providers
        assert "gemini" in providers
        assert "snowflake" in providers
        assert isinstance(providers["openai"], bool)
        assert isinstance(providers["gemini"], bool)
        assert isinstance(providers["snowflake"], bool)


class TestChatEndpoints:
    """Test cases for chat endpoints."""
    
    def test_chat_request_validation(self, client):
        """Test request validation for chat endpoints."""
        # Test empty prompt
        response = client.post("/chat/openai", json={"prompt": ""})
        assert response.status_code == 422
        
        # Test missing prompt
        response = client.post("/chat/openai", json={})
        assert response.status_code == 422
        
        # Test whitespace-only prompt
        response = client.post("/chat/openai", json={"prompt": "   "})
        assert response.status_code == 422
    
    @patch('app.http_client')
    def test_openai_chat_success(self, mock_http_client, client):
        """Test successful OpenAI chat request."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello! How can I help you?"}}],
            "model": "gpt-3.5-turbo",
            "usage": {"total_tokens": 20}
        }
        mock_response.raise_for_status.return_value = None
        mock_http_client.post.return_value = mock_response
        
        # Mock settings to have API key
        with patch.object(settings, 'openai_api_key', 'test-key'):
            response = client.post("/chat/openai", json={"prompt": "Hello"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "openai"
        assert "response" in data
    
    def test_openai_chat_no_api_key(self, client):
        """Test OpenAI chat without API key."""
        with patch.object(settings, 'openai_api_key', None):
            response = client.post("/chat/openai", json={"prompt": "Hello"})
        
        assert response.status_code == 503
        data = response.json()
        assert "not configured" in data["detail"].lower()
    
    @patch('app.http_client')
    def test_gemini_chat_success(self, mock_http_client, client):
        """Test successful Gemini chat request."""
        # Mock the HTTP response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Hello! How can I help you?"}]}}],
            "usageMetadata": {"totalTokenCount": 20}
        }
        mock_response.raise_for_status.return_value = None
        mock_http_client.post.return_value = mock_response
        
        # Mock settings to have API key
        with patch.object(settings, 'gemini_api_key', 'test-key'):
            response = client.post("/chat/gemini", json={"prompt": "Hello"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "gemini"
        assert "response" in data
    
    def test_gemini_chat_no_api_key(self, client):
        """Test Gemini chat without API key."""
        with patch.object(settings, 'gemini_api_key', None):
            response = client.post("/chat/gemini", json={"prompt": "Hello"})
        
        assert response.status_code == 503
        data = response.json()
        assert "not configured" in data["detail"].lower()
    
    def test_snowflake_chat_no_credentials(self, client):
        """Test Snowflake chat without credentials."""
        # Ensure all Snowflake settings are None
        with patch.object(settings, 'snowflake_account', None), \
             patch.object(settings, 'snowflake_user', None), \
             patch.object(settings, 'snowflake_password', None), \
             patch.object(settings, 'snowflake_warehouse', None), \
             patch.object(settings, 'snowflake_database', None), \
             patch.object(settings, 'snowflake_schema', None):
            
            response = client.post("/chat/snowflake", json={"prompt": "Hello"})
        
        assert response.status_code == 503
        data = response.json()
        assert "not configured" in data["detail"].lower()


class TestErrorHandling:
    """Test cases for error handling."""
    
    @patch('app.http_client')
    def test_api_error_handling(self, mock_http_client, client):
        """Test handling of API errors."""
        # Mock HTTP error
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        
        mock_http_client.post.side_effect = httpx.HTTPStatusError(
            "Rate limit exceeded", 
            request=None, 
            response=mock_response
        )
        
        with patch.object(settings, 'openai_api_key', 'test-key'):
            response = client.post("/chat/openai", json={"prompt": "Hello"})
        
        assert response.status_code == 502
        data = response.json()
        assert "error" in data
    
    def test_invalid_endpoint(self, client):
        """Test handling of invalid endpoints."""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_invalid_method(self, client):
        """Test handling of invalid HTTP methods."""
        response = client.get("/chat/openai")  # Should be POST
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__])
