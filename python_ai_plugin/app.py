"""
FastAPI Application for Multi-Provider AI Chat Services

This application provides a unified API interface for multiple AI chat providers:
- OpenAI GPT models
- Google Gemini models
- Snowflake Cortex models

The application follows production-ready practices including:
- Structured error handling
- Environment-based configuration
- Pydantic data validation
- Comprehensive logging
- Clean modular architecture
"""

import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


# =============================================================================
# Configuration and Settings
# =============================================================================

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")

    # Snowflake Cortex Configuration
    snowflake_account: Optional[str] = Field(None, env="SNOWFLAKE_ACCOUNT")
    snowflake_user: Optional[str] = Field(None, env="SNOWFLAKE_USER")
    snowflake_password: Optional[str] = Field(None, env="SNOWFLAKE_PASSWORD")
    snowflake_warehouse: Optional[str] = Field(None, env="SNOWFLAKE_WAREHOUSE")
    snowflake_database: Optional[str] = Field(None, env="SNOWFLAKE_DATABASE")
    snowflake_schema: Optional[str] = Field(None, env="SNOWFLAKE_SCHEMA")

    # API Configuration
    openai_base_url: str = Field("https://api.openai.com/v1", env="OPENAI_BASE_URL")
    gemini_base_url: str = Field("https://generativelanguage.googleapis.com/v1beta", env="GEMINI_BASE_URL")

    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    cors_origins: str = Field("*", env="CORS_ORIGINS")

    class Config:
        env_file = ".env"
        case_sensitive = False


# =============================================================================
# Pydantic Models
# =============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoints."""

    prompt: str = Field(..., min_length=1, max_length=10000, description="The user prompt to send to the AI model")

    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate that prompt is not just whitespace."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or just whitespace")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat endpoints."""

    response: str = Field(..., description="The AI model's response")
    provider: str = Field(..., description="The AI provider that generated the response")
    model: Optional[str] = Field(None, description="The specific model used")
    usage: Optional[Dict[str, Any]] = Field(None, description="Usage statistics if available")


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

# HTTP client for API calls
http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global http_client

    # Startup
    logger.info("Starting FastAPI application...")
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("HTTP client initialized")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")
    if http_client:
        await http_client.aclose()
        logger.info("HTTP client closed")


# =============================================================================
# FastAPI Application Setup
# =============================================================================

app = FastAPI(
    title="Multi-Provider AI Chat API",
    description="A unified API for multiple AI chat providers including OpenAI, Gemini, and Snowflake Cortex",
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

async def call_openai_api(prompt: str) -> ChatResponse:
    """
    Call the OpenAI Chat API with the given prompt.

    Args:
        prompt: The user prompt to send to OpenAI

    Returns:
        ChatResponse: The response from OpenAI

    Raises:
        HTTPException: If the API call fails or API key is missing
    """
    if not settings.openai_api_key:
        logger.error("OpenAI API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured"
        )

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.7
    }

    try:
        logger.info(f"Calling OpenAI API with prompt length: {len(prompt)}")
        response = await http_client.post(
            f"{settings.openai_base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        logger.info("OpenAI API call successful")
        return ChatResponse(
            response=content,
            provider="openai",
            model=data.get("model"),
            usage=data.get("usage")
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"OpenAI API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI API error: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"OpenAI API call failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to call OpenAI API: {str(e)}"
        )


async def call_gemini_api(prompt: str) -> ChatResponse:
    """
    Call the Google Gemini API with the given prompt.

    Args:
        prompt: The user prompt to send to Gemini

    Returns:
        ChatResponse: The response from Gemini

    Raises:
        HTTPException: If the API call fails or API key is missing
    """
    if not settings.gemini_api_key:
        logger.error("Gemini API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key not configured"
        )

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }

    try:
        logger.info(f"Calling Gemini API with prompt length: {len(prompt)}")
        response = await http_client.post(
            f"{settings.gemini_base_url}/models/gemini-pro:generateContent?key={settings.gemini_api_key}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]

        logger.info("Gemini API call successful")
        return ChatResponse(
            response=content,
            provider="gemini",
            model="gemini-pro",
            usage=data.get("usageMetadata")
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API error: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"Gemini API call failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to call Gemini API: {str(e)}"
        )


async def call_snowflake_cortex_api(prompt: str) -> ChatResponse:
    """
    Call the Snowflake Cortex API with the given prompt.

    Args:
        prompt: The user prompt to send to Snowflake Cortex

    Returns:
        ChatResponse: The response from Snowflake Cortex

    Raises:
        HTTPException: If the API call fails or credentials are missing
    """
    required_settings = [
        settings.snowflake_account,
        settings.snowflake_user,
        settings.snowflake_password,
        settings.snowflake_warehouse,
        settings.snowflake_database,
        settings.snowflake_schema
    ]

    if not all(required_settings):
        logger.error("Snowflake Cortex credentials not fully configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Snowflake Cortex credentials not configured"
        )

    # Note: This is a simplified implementation. In production, you would use
    # the official Snowflake connector and proper authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.snowflake_user}:{settings.snowflake_password}"
    }

    # Snowflake Cortex SQL query format
    sql_query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'llama2-70b-chat',
        '{prompt.replace("'", "''")}'
    ) as response;
    """

    payload = {
        "statement": sql_query,
        "warehouse": settings.snowflake_warehouse,
        "database": settings.snowflake_database,
        "schema": settings.snowflake_schema
    }

    try:
        logger.info(f"Calling Snowflake Cortex API with prompt length: {len(prompt)}")

        # Note: This URL structure is simplified. Actual Snowflake REST API
        # endpoints would be different and require proper authentication
        snowflake_url = f"https://{settings.snowflake_account}.snowflakecomputing.com/api/v2/statements"

        response = await http_client.post(
            snowflake_url,
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        # Extract response from Snowflake result format
        content = data.get("data", [{}])[0].get("response", "No response received")

        logger.info("Snowflake Cortex API call successful")
        return ChatResponse(
            response=content,
            provider="snowflake",
            model="llama2-70b-chat",
            usage=None  # Snowflake doesn't provide usage stats in the same format
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Snowflake Cortex API HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Snowflake Cortex API error: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"Snowflake Cortex API call failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to call Snowflake Cortex API: {str(e)}"
        )


def check_provider_availability() -> Dict[str, bool]:
    """
    Check which AI providers are available based on configuration.

    Returns:
        Dict[str, bool]: Provider availability status
    """
    return {
        "openai": bool(settings.openai_api_key),
        "gemini": bool(settings.gemini_api_key),
        "snowflake": all([
            settings.snowflake_account,
            settings.snowflake_user,
            settings.snowflake_password,
            settings.snowflake_warehouse,
            settings.snowflake_database,
            settings.snowflake_schema
        ])
    }


# =============================================================================
# API Endpoints
# =============================================================================

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


@app.post("/chat/openai", response_model=ChatResponse, tags=["Chat"])
async def chat_openai(request: ChatRequest):
    """
    Chat endpoint for OpenAI GPT models.

    Args:
        request: ChatRequest containing the user prompt

    Returns:
        ChatResponse: The response from OpenAI

    Raises:
        HTTPException: If the request is invalid or the API call fails
    """
    logger.info(f"OpenAI chat request received with prompt length: {len(request.prompt)}")

    try:
        response = await call_openai_api(request.prompt)
        logger.info("OpenAI chat request completed successfully")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/chat/gemini", response_model=ChatResponse, tags=["Chat"])
async def chat_gemini(request: ChatRequest):
    """
    Chat endpoint for Google Gemini models.

    Args:
        request: ChatRequest containing the user prompt

    Returns:
        ChatResponse: The response from Gemini

    Raises:
        HTTPException: If the request is invalid or the API call fails
    """
    logger.info(f"Gemini chat request received with prompt length: {len(request.prompt)}")

    try:
        response = await call_gemini_api(request.prompt)
        logger.info("Gemini chat request completed successfully")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Gemini chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/chat/snowflake", response_model=ChatResponse, tags=["Chat"])
async def chat_snowflake(request: ChatRequest):
    """
    Chat endpoint for Snowflake Cortex models.

    Args:
        request: ChatRequest containing the user prompt

    Returns:
        ChatResponse: The response from Snowflake Cortex

    Raises:
        HTTPException: If the request is invalid or the API call fails
    """
    logger.info(f"Snowflake chat request received with prompt length: {len(request.prompt)}")

    try:
        response = await call_snowflake_cortex_api(request.prompt)
        logger.info("Snowflake chat request completed successfully")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Snowflake chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(_request, exc: HTTPException):
    """
    Custom HTTP exception handler for consistent error responses.

    Args:
        request: The incoming request
        exc: The HTTPException that was raised

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request, exc: Exception):
    """
    General exception handler for unexpected errors.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "status_code": 500
        }
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