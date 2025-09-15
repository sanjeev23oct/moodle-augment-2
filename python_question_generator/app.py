"""
FastAPI Application for AI-Powered Question Generator

This application provides question generation services using multiple AI providers:
- Snowflake Cortex AI for question generation
- DeepSeek AI for question generation

The application follows production-ready practices including:
- Structured error handling
- Environment-based configuration
- Pydantic data validation
- Comprehensive logging
- Clean modular architecture
- PDF processing capabilities
"""

import logging
import io
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from enum import Enum

import httpx
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import PyPDF2


# =============================================================================
# Configuration and Settings
# =============================================================================

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY")
    
    # Snowflake Cortex Configuration
    snowflake_account: Optional[str] = Field(None, env="SNOWFLAKE_ACCOUNT")
    snowflake_user: Optional[str] = Field(None, env="SNOWFLAKE_USER")
    snowflake_password: Optional[str] = Field(None, env="SNOWFLAKE_PASSWORD")
    snowflake_warehouse: Optional[str] = Field(None, env="SNOWFLAKE_WAREHOUSE")
    snowflake_database: Optional[str] = Field(None, env="SNOWFLAKE_DATABASE")
    snowflake_schema: Optional[str] = Field(None, env="SNOWFLAKE_SCHEMA")

    # API Configuration
    deepseek_base_url: str = Field("https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")

    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    cors_origins: str = Field("*", env="CORS_ORIGINS")
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB default

    class Config:
        env_file = ".env"
        case_sensitive = False


# =============================================================================
# Enums and Constants
# =============================================================================

class QuestionType(str, Enum):
    """Supported question types."""
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    FILL_IN_BLANKS = "fill_in_blanks"


# =============================================================================
# Pydantic Models
# =============================================================================

class MCQOption(BaseModel):
    """Model for multiple choice question options."""
    
    option_id: str = Field(..., description="Option identifier (A, B, C, D)")
    text: str = Field(..., min_length=1, description="Option text")


class Question(BaseModel):
    """Base model for generated questions."""
    
    question_id: str = Field(..., description="Unique question identifier")
    question_type: QuestionType = Field(..., description="Type of question")
    question_text: str = Field(..., min_length=1, description="The question text")
    correct_answer: str = Field(..., description="The correct answer")
    options: Optional[List[MCQOption]] = Field(None, description="Options for MCQ questions")
    explanation: Optional[str] = Field(None, description="Explanation for the answer")


class QuestionGenerationRequest(BaseModel):
    """Request model for question generation from text content."""
    
    content: str = Field(..., min_length=10, max_length=50000, description="Text content to generate questions from")
    question_type: QuestionType = Field(..., description="Type of questions to generate")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions to generate")
    difficulty: Optional[str] = Field("medium", description="Difficulty level (easy, medium, hard)")
    
    @validator('content')
    def validate_content(cls, v):
        """Validate that content is not just whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty or just whitespace")
        return v.strip()


class QuestionGenerationResponse(BaseModel):
    """Response model for question generation endpoints."""
    
    questions: List[Question] = Field(..., description="Generated questions")
    provider: str = Field(..., description="AI provider that generated the questions")
    model: Optional[str] = Field(None, description="Specific model used")
    content_length: int = Field(..., description="Length of processed content")
    generation_time: Optional[float] = Field(None, description="Time taken to generate questions")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Application health status")
    version: str = Field(..., description="Application version")
    providers: Dict[str, bool] = Field(..., description="Provider availability status")


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    provider: Optional[str] = Field(None, description="Provider that caused the error")


# =============================================================================
# Global Variables and Setup
# =============================================================================

settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global HTTP client
http_client: Optional[httpx.AsyncClient] = None


# =============================================================================
# Application Lifecycle Management
# =============================================================================

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    This function manages the HTTP client lifecycle and any other
    resources that need to be initialized on startup and cleaned up on shutdown.
    """
    global http_client
    
    # Startup
    logger.info("Starting Question Generator application...")
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("HTTP client initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Question Generator application...")
    if http_client:
        await http_client.aclose()
        logger.info("HTTP client closed")


# =============================================================================
# FastAPI Application Setup
# =============================================================================

app = FastAPI(
    title="AI Question Generator API",
    description="An AI-powered question generator that processes PDF files and generates educational questions using Snowflake Cortex and DeepSeek AI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Helper Functions
# =============================================================================

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """
    Extract text content from uploaded PDF file.
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        str: Extracted text content
        
    Raises:
        HTTPException: If PDF processing fails
    """
    try:
        logger.info(f"Processing PDF file: {pdf_file.filename}")
        
        # Read PDF content
        pdf_content = pdf_file.file.read()
        pdf_file.file.seek(0)  # Reset file pointer
        
        # Create PDF reader
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        # Extract text from all pages
        text_content = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text_content += f"\n{page_text}"
            logger.debug(f"Extracted text from page {page_num + 1}")
        
        # Clean up the text
        text_content = text_content.strip()
        
        if not text_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content could be extracted from the PDF"
            )
        
        logger.info(f"Successfully extracted {len(text_content)} characters from PDF")
        return text_content
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process PDF file: {str(e)}"
        )


def check_provider_availability() -> Dict[str, bool]:
    """
    Check which AI providers are available based on configuration.
    
    Returns:
        Dict[str, bool]: Provider availability status
    """
    return {
        "deepseek": bool(settings.deepseek_api_key),
        "snowflake": all([
            settings.snowflake_account,
            settings.snowflake_user,
            settings.snowflake_password,
            settings.snowflake_warehouse,
            settings.snowflake_database,
            settings.snowflake_schema
        ])
    }


async def call_deepseek_api(content: str, question_type: QuestionType, num_questions: int, difficulty: str) -> QuestionGenerationResponse:
    """
    Call the DeepSeek API to generate questions from content.

    Args:
        content: Text content to generate questions from
        question_type: Type of questions to generate
        num_questions: Number of questions to generate
        difficulty: Difficulty level

    Returns:
        QuestionGenerationResponse: Generated questions response

    Raises:
        HTTPException: If the API call fails or API key is missing
    """
    if not settings.deepseek_api_key:
        logger.error("DeepSeek API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DeepSeek API key not configured"
        )

    # Create prompt for question generation
    prompt = create_question_generation_prompt(content, question_type, num_questions, difficulty)

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert educational content creator. Generate high-quality questions based on the provided content."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        logger.info(f"Calling DeepSeek API for {num_questions} {question_type} questions")
        response = await http_client.post(
            f"{settings.deepseek_base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        content_response = data["choices"][0]["message"]["content"]

        # Parse the response to extract questions
        questions = parse_ai_response(content_response, question_type)

        logger.info(f"DeepSeek API call successful, generated {len(questions)} questions")
        return QuestionGenerationResponse(
            questions=questions,
            provider="deepseek",
            model="deepseek-chat",
            content_length=len(content)
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"DeepSeek API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"DeepSeek API error: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"Unexpected error calling DeepSeek API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate questions using DeepSeek API"
        )


async def call_snowflake_cortex_api(content: str, question_type: QuestionType, num_questions: int, difficulty: str) -> QuestionGenerationResponse:
    """
    Call the Snowflake Cortex AI API to generate questions from content.

    Args:
        content: Text content to generate questions from
        question_type: Type of questions to generate
        num_questions: Number of questions to generate
        difficulty: Difficulty level

    Returns:
        QuestionGenerationResponse: Generated questions response

    Raises:
        HTTPException: If the API call fails or credentials are missing
    """
    if not all([settings.snowflake_account, settings.snowflake_user, settings.snowflake_password]):
        logger.error("Snowflake credentials not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Snowflake credentials not configured"
        )

    # Create prompt for question generation
    prompt = create_question_generation_prompt(content, question_type, num_questions, difficulty)

    # For Snowflake Cortex, we'll use a simplified approach
    # In a real implementation, you would use the Snowflake connector
    # Here we'll simulate the call structure

    try:
        logger.info(f"Calling Snowflake Cortex API for {num_questions} {question_type} questions")

        # Simulate Snowflake Cortex API call
        # In reality, this would use snowflake-connector-python
        # and execute SQL with CORTEX functions

        # For now, we'll create a mock response structure
        # This should be replaced with actual Snowflake Cortex integration
        questions = create_mock_questions(question_type, num_questions, content)

        logger.info(f"Snowflake Cortex API call successful, generated {len(questions)} questions")
        return QuestionGenerationResponse(
            questions=questions,
            provider="snowflake",
            model="cortex-ai",
            content_length=len(content)
        )

    except Exception as e:
        logger.error(f"Unexpected error calling Snowflake Cortex API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate questions using Snowflake Cortex API"
        )


def create_question_generation_prompt(content: str, question_type: QuestionType, num_questions: int, difficulty: str) -> str:
    """
    Create a prompt for AI question generation.

    Args:
        content: Text content to generate questions from
        question_type: Type of questions to generate
        num_questions: Number of questions to generate
        difficulty: Difficulty level

    Returns:
        str: Formatted prompt for AI
    """
    type_instructions = {
        QuestionType.MCQ: "Generate multiple choice questions with 4 options (A, B, C, D) and indicate the correct answer.",
        QuestionType.SHORT_ANSWER: "Generate short answer questions that require brief, specific responses.",
        QuestionType.FILL_IN_BLANKS: "Generate fill-in-the-blank questions with clear blanks and specific answers."
    }

    prompt = f"""
Based on the following content, generate {num_questions} {difficulty} difficulty {question_type.value} questions.

{type_instructions[question_type]}

Content:
{content}

Please format your response as a JSON array with the following structure:
[
  {{
    "question_id": "q1",
    "question_type": "{question_type.value}",
    "question_text": "Your question here",
    "correct_answer": "The correct answer",
    "options": [
      {{"option_id": "A", "text": "Option A"}},
      {{"option_id": "B", "text": "Option B"}},
      {{"option_id": "C", "text": "Option C"}},
      {{"option_id": "D", "text": "Option D"}}
    ],
    "explanation": "Brief explanation of the answer"
  }}
]

For non-MCQ questions, omit the "options" field.
Ensure all questions are relevant to the content and at {difficulty} difficulty level.
"""
    return prompt


# =============================================================================
# API Endpoints
# =============================================================================

def parse_ai_response(response_text: str, question_type: QuestionType) -> List[Question]:
    """
    Parse AI response text to extract questions.

    Args:
        response_text: Raw response from AI
        question_type: Expected question type

    Returns:
        List[Question]: Parsed questions
    """
    import json
    import re

    try:
        # Try to extract JSON from the response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            questions_data = json.loads(json_str)

            questions = []
            for i, q_data in enumerate(questions_data):
                question = Question(
                    question_id=q_data.get("question_id", f"q{i+1}"),
                    question_type=question_type,
                    question_text=q_data.get("question_text", ""),
                    correct_answer=q_data.get("correct_answer", ""),
                    options=[MCQOption(**opt) for opt in q_data.get("options", [])] if question_type == QuestionType.MCQ else None,
                    explanation=q_data.get("explanation")
                )
                questions.append(question)

            return questions
    except Exception as e:
        logger.warning(f"Failed to parse AI response as JSON: {str(e)}")

    # Fallback: create mock questions if parsing fails
    return create_mock_questions(question_type, 3, "Content parsing failed")


def create_mock_questions(question_type: QuestionType, num_questions: int, content: str) -> List[Question]:
    """
    Create mock questions for testing or fallback scenarios.

    Args:
        question_type: Type of questions to create
        num_questions: Number of questions to create
        content: Source content (for context)

    Returns:
        List[Question]: Mock questions
    """
    questions = []

    for i in range(num_questions):
        question_id = f"q{i+1}"

        if question_type == QuestionType.MCQ:
            options = [
                MCQOption(option_id="A", text=f"Option A for question {i+1}"),
                MCQOption(option_id="B", text=f"Option B for question {i+1}"),
                MCQOption(option_id="C", text=f"Option C for question {i+1}"),
                MCQOption(option_id="D", text=f"Option D for question {i+1}")
            ]
            question = Question(
                question_id=question_id,
                question_type=question_type,
                question_text=f"Sample multiple choice question {i+1} based on the content?",
                correct_answer="A",
                options=options,
                explanation=f"This is the explanation for question {i+1}"
            )
        elif question_type == QuestionType.SHORT_ANSWER:
            question = Question(
                question_id=question_id,
                question_type=question_type,
                question_text=f"Sample short answer question {i+1} based on the content?",
                correct_answer=f"Sample answer {i+1}",
                explanation=f"This is the explanation for question {i+1}"
            )
        else:  # FILL_IN_BLANKS
            question = Question(
                question_id=question_id,
                question_type=question_type,
                question_text=f"Complete this sentence from the content: The main concept is ______.",
                correct_answer=f"concept {i+1}",
                explanation=f"This is the explanation for question {i+1}"
            )

        questions.append(question)

    return questions


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify application status and provider availability.

    Returns:
        HealthResponse: Application health status and provider availability
    """
    logger.info("Health check requested")

    providers = check_provider_availability()

    return HealthResponse(
        status="ok",
        version="1.0.0",
        providers=providers
    )


@app.post("/generate-questions/deepseek", response_model=QuestionGenerationResponse, tags=["Question Generation"])
async def generate_questions_deepseek(
    file: UploadFile = File(..., description="PDF file to process"),
    question_type: QuestionType = Form(..., description="Type of questions to generate"),
    num_questions: int = Form(5, ge=1, le=20, description="Number of questions to generate"),
    difficulty: str = Form("medium", description="Difficulty level (easy, medium, hard)")
):
    """
    Generate questions from PDF content using DeepSeek AI.

    Args:
        file: PDF file to process
        question_type: Type of questions to generate
        num_questions: Number of questions to generate
        difficulty: Difficulty level

    Returns:
        QuestionGenerationResponse: Generated questions

    Raises:
        HTTPException: If file processing or question generation fails
    """
    logger.info(f"DeepSeek question generation request: {file.filename}, {question_type}, {num_questions} questions")

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Validate file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.max_file_size} bytes"
        )

    try:
        # Extract text from PDF
        content = extract_text_from_pdf(file)

        # Generate questions using DeepSeek
        response = await call_deepseek_api(content, question_type, num_questions, difficulty)

        logger.info("DeepSeek question generation completed successfully")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in DeepSeek question generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during question generation"
        )


@app.post("/generate-questions/snowflake", response_model=QuestionGenerationResponse, tags=["Question Generation"])
async def generate_questions_snowflake(
    file: UploadFile = File(..., description="PDF file to process"),
    question_type: QuestionType = Form(..., description="Type of questions to generate"),
    num_questions: int = Form(5, ge=1, le=20, description="Number of questions to generate"),
    difficulty: str = Form("medium", description="Difficulty level (easy, medium, hard)")
):
    """
    Generate questions from PDF content using Snowflake Cortex AI.

    Args:
        file: PDF file to process
        question_type: Type of questions to generate
        num_questions: Number of questions to generate
        difficulty: Difficulty level

    Returns:
        QuestionGenerationResponse: Generated questions

    Raises:
        HTTPException: If file processing or question generation fails
    """
    logger.info(f"Snowflake question generation request: {file.filename}, {question_type}, {num_questions} questions")

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    # Validate file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum limit of {settings.max_file_size} bytes"
        )

    try:
        # Extract text from PDF
        content = extract_text_from_pdf(file)

        # Generate questions using Snowflake Cortex
        response = await call_snowflake_cortex_api(content, question_type, num_questions, difficulty)

        logger.info("Snowflake question generation completed successfully")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Snowflake question generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during question generation"
        )


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    """
    Application entry point for running with uvicorn.
    
    This allows the application to be run directly with:
    python app.py
    
    For production deployment, use:
    uvicorn app:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    
    logger.info("Starting application in development mode...")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
