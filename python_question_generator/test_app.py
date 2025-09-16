"""
Test suite for the AI Question Generator API

This module contains comprehensive tests for all endpoints and functionality
of the question generator application.
"""

import pytest
import io
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app import app, settings, QuestionType

# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for the health check endpoint."""
    
    def test_health_check_success(self):
        """Test successful health check."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert "providers" in data
        assert "deepseek" in data["providers"]
        assert "snowflake" in data["providers"]


class TestPDFProcessing:
    """Test cases for PDF processing functionality."""
    
    def test_pdf_upload_invalid_file_type(self):
        """Test upload with non-PDF file."""
        # Create a fake text file
        fake_file = io.BytesIO(b"This is not a PDF")
        
        response = client.post(
            "/generate-questions/deepseek",
            files={"file": ("test.txt", fake_file, "text/plain")},
            data={
                "question_type": "mcq",
                "num_questions": 5,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 400
        assert "Only PDF files are supported" in response.json()["detail"]
    
    def test_missing_both_file_and_text(self):
        """Test request without both file and text content."""
        response = client.post(
            "/generate-questions/deepseek",
            data={
                "question_type": "mcq",
                "num_questions": 5,
                "difficulty": "medium"
            }
        )

        assert response.status_code == 400
        assert "Either a PDF file or text content must be provided" in response.json()["detail"]

    def test_both_file_and_text_provided(self):
        """Test request with both file and text content."""
        fake_file = io.BytesIO(b"Fake PDF content")

        response = client.post(
            "/generate-questions/deepseek",
            files={"file": ("test.pdf", fake_file, "application/pdf")},
            data={
                "question_type": "mcq",
                "num_questions": 5,
                "difficulty": "medium",
                "text_content": "Some text content"
            }
        )

        assert response.status_code == 400
        assert "Please provide either a PDF file or text content, not both" in response.json()["detail"]


class TestQuestionGeneration:
    """Test cases for question generation endpoints."""
    
    @patch('app.extract_text_from_pdf')
    @patch('app.call_deepseek_api')
    def test_deepseek_question_generation_success(self, mock_deepseek_api, mock_extract_text):
        """Test successful question generation with DeepSeek."""
        # Mock PDF text extraction
        mock_extract_text.return_value = "Sample PDF content for testing"
        
        # Mock DeepSeek API response
        from app import QuestionGenerationResponse, Question, MCQOption
        mock_questions = [
            Question(
                question_id="q1",
                question_type=QuestionType.MCQ,
                question_text="What is the main topic?",
                correct_answer="A",
                options=[
                    MCQOption(option_id="A", text="Correct answer"),
                    MCQOption(option_id="B", text="Wrong answer 1"),
                    MCQOption(option_id="C", text="Wrong answer 2"),
                    MCQOption(option_id="D", text="Wrong answer 3")
                ],
                explanation="This is the explanation"
            )
        ]
        
        mock_response = QuestionGenerationResponse(
            questions=mock_questions,
            provider="deepseek",
            model="deepseek-chat",
            content_length=100
        )
        mock_deepseek_api.return_value = mock_response
        
        # Create a fake PDF file
        fake_pdf = io.BytesIO(b"Fake PDF content")
        
        response = client.post(
            "/generate-questions/deepseek",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={
                "question_type": "mcq",
                "num_questions": 1,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "deepseek"
        assert len(data["questions"]) == 1
        assert data["questions"][0]["question_type"] == "mcq"
    
    @patch('app.extract_text_from_pdf')
    @patch('app.call_snowflake_cortex_api')
    def test_snowflake_question_generation_success(self, mock_snowflake_api, mock_extract_text):
        """Test successful question generation with Snowflake."""
        # Mock PDF text extraction
        mock_extract_text.return_value = "Sample PDF content for testing"
        
        # Mock Snowflake API response
        from app import QuestionGenerationResponse, Question
        mock_questions = [
            Question(
                question_id="q1",
                question_type=QuestionType.SHORT_ANSWER,
                question_text="Explain the main concept.",
                correct_answer="The main concept is...",
                explanation="This is the explanation"
            )
        ]
        
        mock_response = QuestionGenerationResponse(
            questions=mock_questions,
            provider="snowflake",
            model="cortex-ai",
            content_length=100
        )
        mock_snowflake_api.return_value = mock_response
        
        # Create a fake PDF file
        fake_pdf = io.BytesIO(b"Fake PDF content")
        
        response = client.post(
            "/generate-questions/snowflake",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={
                "question_type": "short_answer",
                "num_questions": 1,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "snowflake"
        assert len(data["questions"]) == 1
        assert data["questions"][0]["question_type"] == "short_answer"
    
    def test_invalid_question_type(self):
        """Test with invalid question type."""
        fake_pdf = io.BytesIO(b"Fake PDF content")
        
        response = client.post(
            "/generate-questions/deepseek",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={
                "question_type": "invalid_type",
                "num_questions": 1,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_num_questions(self):
        """Test with invalid number of questions."""
        fake_pdf = io.BytesIO(b"Fake PDF content")
        
        response = client.post(
            "/generate-questions/deepseek",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={
                "question_type": "mcq",
                "num_questions": 25,  # Exceeds maximum
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 422  # Validation error

    @patch('app.call_deepseek_api')
    def test_text_input_success(self, mock_deepseek_api):
        """Test successful question generation with text input."""
        # Mock DeepSeek API response
        from app import QuestionGenerationResponse, Question
        mock_questions = [
            Question(
                question_id="q1",
                question_type=QuestionType.SHORT_ANSWER,
                question_text="What is the main concept?",
                correct_answer="The main concept is...",
                explanation="This is the explanation"
            )
        ]

        mock_response = QuestionGenerationResponse(
            questions=mock_questions,
            provider="deepseek",
            model="deepseek-chat",
            content_length=100
        )
        mock_deepseek_api.return_value = mock_response

        response = client.post(
            "/generate-questions/deepseek",
            data={
                "question_type": "short_answer",
                "num_questions": 1,
                "difficulty": "medium",
                "text_content": "This is sample educational content for testing question generation."
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "deepseek"
        assert len(data["questions"]) == 1
        assert data["questions"][0]["question_type"] == "short_answer"

    def test_text_input_too_short(self):
        """Test with text content that is too short."""
        response = client.post(
            "/generate-questions/deepseek",
            data={
                "question_type": "mcq",
                "num_questions": 1,
                "difficulty": "medium",
                "text_content": "Short"
            }
        )

        assert response.status_code == 400
        assert "Text content must be at least 10 characters long" in response.json()["detail"]


class TestJSONEndpoints:
    """Test cases for JSON-based endpoints."""

    @patch('app.call_deepseek_api')
    def test_deepseek_json_endpoint_success(self, mock_deepseek_api):
        """Test successful question generation with JSON endpoint."""
        # Mock DeepSeek API response
        from app import QuestionGenerationResponse, Question
        mock_questions = [
            Question(
                question_id="q1",
                question_type=QuestionType.MCQ,
                question_text="What is the main topic?",
                correct_answer="A",
                options=[
                    MCQOption(option_id="A", text="Correct answer"),
                    MCQOption(option_id="B", text="Wrong answer 1"),
                    MCQOption(option_id="C", text="Wrong answer 2"),
                    MCQOption(option_id="D", text="Wrong answer 3")
                ],
                explanation="This is the explanation"
            )
        ]

        mock_response = QuestionGenerationResponse(
            questions=mock_questions,
            provider="deepseek",
            model="deepseek-chat",
            content_length=100
        )
        mock_deepseek_api.return_value = mock_response

        response = client.post(
            "/generate-questions/deepseek/json",
            json={
                "content": "This is sample educational content for testing question generation with sufficient length.",
                "question_type": "mcq",
                "num_questions": 1,
                "difficulty": "medium"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "deepseek"
        assert len(data["questions"]) == 1
        assert data["questions"][0]["question_type"] == "mcq"

    def test_json_endpoint_validation_error(self):
        """Test JSON endpoint with invalid data."""
        response = client.post(
            "/generate-questions/deepseek/json",
            json={
                "content": "Short",  # Too short
                "question_type": "mcq",
                "num_questions": 1,
                "difficulty": "medium"
            }
        )

        assert response.status_code == 422  # Validation error


class TestErrorHandling:
    """Test cases for error handling scenarios."""
    
    @patch('app.extract_text_from_pdf')
    def test_pdf_extraction_error(self, mock_extract_text):
        """Test error during PDF text extraction."""
        mock_extract_text.side_effect = Exception("PDF processing failed")
        
        fake_pdf = io.BytesIO(b"Fake PDF content")
        
        response = client.post(
            "/generate-questions/deepseek",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={
                "question_type": "mcq",
                "num_questions": 1,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 500
    
    @patch('app.extract_text_from_pdf')
    @patch('app.call_deepseek_api')
    def test_api_call_error(self, mock_deepseek_api, mock_extract_text):
        """Test error during API call."""
        mock_extract_text.return_value = "Sample content"
        mock_deepseek_api.side_effect = Exception("API call failed")
        
        fake_pdf = io.BytesIO(b"Fake PDF content")
        
        response = client.post(
            "/generate-questions/deepseek",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            data={
                "question_type": "mcq",
                "num_questions": 1,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 500


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_check_provider_availability(self):
        """Test provider availability checking."""
        from app import check_provider_availability
        
        providers = check_provider_availability()
        assert isinstance(providers, dict)
        assert "deepseek" in providers
        assert "snowflake" in providers
        assert isinstance(providers["deepseek"], bool)
        assert isinstance(providers["snowflake"], bool)
    
    def test_create_question_generation_prompt(self):
        """Test prompt creation for question generation."""
        from app import create_question_generation_prompt, QuestionType
        
        prompt = create_question_generation_prompt(
            "Sample content",
            QuestionType.MCQ,
            5,
            "medium"
        )
        
        assert isinstance(prompt, str)
        assert "Sample content" in prompt
        assert "5" in prompt
        assert "medium" in prompt
        assert "mcq" in prompt
    
    def test_create_mock_questions(self):
        """Test mock question creation."""
        from app import create_mock_questions, QuestionType
        
        questions = create_mock_questions(QuestionType.MCQ, 3, "Sample content")
        
        assert len(questions) == 3
        assert all(q.question_type == QuestionType.MCQ for q in questions)
        assert all(q.options is not None for q in questions)
        assert all(len(q.options) == 4 for q in questions)


if __name__ == "__main__":
    pytest.main([__file__])
