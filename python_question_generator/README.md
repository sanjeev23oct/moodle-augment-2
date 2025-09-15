# AI Question Generator API

A production-ready FastAPI application that generates educational questions from PDF content using multiple AI providers including Snowflake Cortex and DeepSeek AI.

## Features

- **PDF Processing**: Extract text content from uploaded PDF files
- **Multiple Question Types**: Support for MCQ, Short Answer, and Fill-in-the-Blanks questions
- **Multiple AI Providers**: Support for Snowflake Cortex AI and DeepSeek AI
- **Production Ready**: Comprehensive error handling, logging, and monitoring
- **Type Safety**: Full Pydantic validation and type hints
- **Environment Configuration**: Secure credential management via environment variables
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Checks**: Built-in health monitoring and provider availability checks
- **Async/Await**: High-performance asynchronous request handling

## Quick Start

### 1. Installation

```bash
# Clone the repository
cd python_question_generator

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual API credentials:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

### 3. Running the Application

```bash
# Development mode
python app.py

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns application status and provider availability

### Question Generation with DeepSeek
- **POST** `/generate-questions/deepseek`
- Upload PDF file and generate questions using DeepSeek AI
- Form data:
  - `file`: PDF file (required)
  - `question_type`: "mcq", "short_answer", or "fill_in_blanks" (required)
  - `num_questions`: Number of questions (1-20, default: 5)
  - `difficulty`: "easy", "medium", or "hard" (default: "medium")

### Question Generation with Snowflake Cortex
- **POST** `/generate-questions/snowflake`
- Upload PDF file and generate questions using Snowflake Cortex AI
- Same form data as DeepSeek endpoint

## API Documentation

Once running, visit:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Generate MCQ questions using DeepSeek
curl -X POST "http://localhost:8000/generate-questions/deepseek" \
  -F "file=@sample.pdf" \
  -F "question_type=mcq" \
  -F "num_questions=5" \
  -F "difficulty=medium"
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Generate questions
with open("sample.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "question_type": "mcq",
        "num_questions": 5,
        "difficulty": "medium"
    }
    response = requests.post(
        "http://localhost:8000/generate-questions/deepseek",
        files=files,
        data=data
    )
    print(response.json())
```

## Response Format

### Question Generation Response

```json
{
  "questions": [
    {
      "question_id": "q1",
      "question_type": "mcq",
      "question_text": "What is the main concept discussed?",
      "correct_answer": "A",
      "options": [
        {"option_id": "A", "text": "Correct answer"},
        {"option_id": "B", "text": "Option B"},
        {"option_id": "C", "text": "Option C"},
        {"option_id": "D", "text": "Option D"}
      ],
      "explanation": "This is why A is correct..."
    }
  ],
  "provider": "deepseek",
  "model": "deepseek-chat",
  "content_length": 1500,
  "generation_time": 2.5
}
```

## Configuration Options

### Environment Variables

- `DEEPSEEK_API_KEY`: API key for DeepSeek AI
- `DEEPSEEK_BASE_URL`: Base URL for DeepSeek API (default: https://api.deepseek.com/v1)
- `SNOWFLAKE_ACCOUNT`: Snowflake account identifier
- `SNOWFLAKE_USER`: Snowflake username
- `SNOWFLAKE_PASSWORD`: Snowflake password
- `SNOWFLAKE_WAREHOUSE`: Snowflake warehouse name
- `SNOWFLAKE_DATABASE`: Snowflake database name
- `SNOWFLAKE_SCHEMA`: Snowflake schema name
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `MAX_FILE_SIZE`: Maximum PDF file size in bytes (default: 10MB)

## Docker Deployment

### Build Docker Image

```bash
docker build -t python-question-generator:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e DEEPSEEK_API_KEY=your_key \
  -e SNOWFLAKE_ACCOUNT=your_account \
  python-question-generator:latest
```

## Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- `400 Bad Request`: Invalid input, unsupported file type, or file too large
- `413 Request Entity Too Large`: File size exceeds maximum limit
- `500 Internal Server Error`: Unexpected server errors
- `502 Bad Gateway`: AI provider API errors
- `503 Service Unavailable`: AI provider not configured

## Supported Question Types

1. **Multiple Choice Questions (MCQ)**
   - 4 options (A, B, C, D)
   - Single correct answer
   - Explanation provided

2. **Short Answer Questions**
   - Brief, specific responses required
   - Correct answer provided
   - Explanation included

3. **Fill-in-the-Blanks**
   - Sentences with missing words/phrases
   - Specific answers required
   - Context-based questions

## Limitations

- PDF files only (no other document formats)
- Maximum file size: 10MB (configurable)
- Maximum 20 questions per request
- Text-based PDFs only (no OCR for scanned documents)

## Contributing

1. Follow the existing code style and patterns
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

This project follows the same license as the parent repository.
