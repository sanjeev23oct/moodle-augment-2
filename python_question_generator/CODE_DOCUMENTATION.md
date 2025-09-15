# Code Documentation: AI Question Generator API

## Overview

This document provides a detailed explanation of the FastAPI application implementation for the AI Question Generator, covering architecture, design patterns, and best practices used in `app.py`.

## Architecture Overview

The application follows a clean, modular architecture with clear separation of concerns:

```
app.py
├── Configuration & Settings
├── Enums & Constants
├── Pydantic Models
├── Application Setup
├── Helper Functions (PDF Processing & AI Clients)
├── API Endpoints
└── Entry Point
```

## Detailed Implementation Analysis

### 1. Configuration Management

```python
class Settings(BaseSettings):
    # Environment-based configuration
```

**Design Decisions:**
- Uses Pydantic Settings for type-safe configuration
- Environment variables provide secure credential management
- Optional fields allow partial provider configuration
- Default values ensure application can start without full configuration

**Best Practices:**
- Separation of configuration from code
- Type hints for all settings
- Clear environment variable naming convention
- Support for `.env` files in development

### 2. Data Models

#### Question Models
```python
class Question(BaseModel):
    question_id: str
    question_type: QuestionType
    question_text: str
    correct_answer: str
    options: Optional[List[MCQOption]]
    explanation: Optional[str]
```

**Design Decisions:**
- Pydantic models ensure type safety and validation
- Flexible structure supports multiple question types
- Optional fields for extensibility
- Descriptive field documentation for API docs

**Best Practices:**
- Input validation at the model level
- Clear error messages for validation failures
- Consistent response structure across all endpoints
- Enum usage for controlled vocabularies

### 3. PDF Processing

```python
def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    # PDF text extraction using PyPDF2
```

**Design Decisions:**
- Uses PyPDF2 for reliable PDF text extraction
- Handles file upload validation and size limits
- Comprehensive error handling for various PDF issues
- Memory-efficient processing with file streams

**Best Practices:**
- File type validation before processing
- Size limit enforcement for security
- Proper resource cleanup
- Detailed logging for debugging

### 4. AI Provider Integration

#### DeepSeek API Integration
```python
async def call_deepseek_api(content: str, question_type: QuestionType, 
                           num_questions: int, difficulty: str) -> QuestionGenerationResponse:
    # DeepSeek API call implementation
```

**Design Decisions:**
- Async/await for non-blocking I/O operations
- Structured prompt engineering for consistent results
- Comprehensive error handling with appropriate HTTP status codes
- Response parsing with fallback mechanisms

#### Snowflake Cortex Integration
```python
async def call_snowflake_cortex_api(content: str, question_type: QuestionType,
                                   num_questions: int, difficulty: str) -> QuestionGenerationResponse:
    # Snowflake Cortex API call implementation
```

**Design Decisions:**
- Placeholder implementation for Snowflake Cortex integration
- Consistent interface with other AI providers
- Mock response generation for testing and development
- Extensible design for future Snowflake connector integration

### 5. Prompt Engineering

```python
def create_question_generation_prompt(content: str, question_type: QuestionType,
                                    num_questions: int, difficulty: str) -> str:
    # Structured prompt creation
```

**Design Decisions:**
- Template-based prompt generation
- Question type-specific instructions
- JSON response format specification
- Difficulty level integration

**Best Practices:**
- Clear, structured prompts for consistent AI responses
- Format specification to ensure parseable responses
- Context-aware instruction generation
- Extensible template system

### 6. Response Parsing

```python
def parse_ai_response(response_text: str, question_type: QuestionType) -> List[Question]:
    # AI response parsing with fallback
```

**Design Decisions:**
- JSON extraction from AI responses
- Robust error handling with fallback mechanisms
- Type-safe object creation
- Graceful degradation for parsing failures

### 7. API Endpoints

#### File Upload Endpoints
```python
@app.post("/generate-questions/deepseek", response_model=QuestionGenerationResponse)
async def generate_questions_deepseek(
    file: UploadFile = File(...),
    question_type: QuestionType = Form(...),
    num_questions: int = Form(5, ge=1, le=20),
    difficulty: str = Form("medium")
):
```

**Design Decisions:**
- Form-based file upload with additional parameters
- Comprehensive input validation
- Consistent error handling across endpoints
- Detailed logging for monitoring and debugging

**Best Practices:**
- File type and size validation
- Parameter validation with Pydantic
- Appropriate HTTP status codes
- Structured error responses

### 8. Error Handling Strategy

The application implements multi-layered error handling:

1. **Input Validation**: Pydantic models validate all inputs
2. **Business Logic Errors**: Custom exceptions for domain-specific errors
3. **External API Errors**: HTTP status code mapping and retry logic
4. **System Errors**: Graceful degradation and logging

### 9. Logging Strategy

```python
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

**Implementation:**
- Structured logging with timestamps
- Configurable log levels
- Request/response logging for debugging
- Error context preservation

### 10. Testing Strategy

The application includes comprehensive tests:

- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Mock Testing**: External dependency mocking
- **Error Scenario Testing**: Edge case handling

## Security Considerations

1. **File Upload Security**:
   - File type validation
   - Size limit enforcement
   - Content scanning (PDF structure validation)

2. **API Security**:
   - Input validation and sanitization
   - Rate limiting considerations
   - CORS configuration

3. **Credential Management**:
   - Environment variable usage
   - No hardcoded secrets
   - Secure credential storage

## Performance Optimizations

1. **Async Processing**: Non-blocking I/O operations
2. **Memory Management**: Efficient file handling
3. **Connection Pooling**: HTTP client reuse
4. **Caching Opportunities**: Response caching for identical requests

## Scalability Considerations

1. **Horizontal Scaling**: Stateless design enables multiple instances
2. **Resource Management**: Configurable limits and timeouts
3. **Load Balancing**: Health check endpoint for load balancer integration
4. **Monitoring**: Comprehensive logging for observability

## Future Enhancements

1. **Additional AI Providers**: Extensible provider architecture
2. **Question Type Extensions**: New question formats
3. **Advanced PDF Processing**: OCR support for scanned documents
4. **Caching Layer**: Redis integration for response caching
5. **Rate Limiting**: Request throttling implementation
6. **Authentication**: API key or OAuth integration

## Deployment Considerations

1. **Docker Containerization**: Multi-stage builds for optimization
2. **Environment Configuration**: Production-ready settings
3. **Health Monitoring**: Comprehensive health checks
4. **Logging Integration**: Centralized logging systems
5. **Metrics Collection**: Application performance monitoring

This architecture provides a solid foundation for a production-ready question generation service while maintaining flexibility for future enhancements and integrations.
