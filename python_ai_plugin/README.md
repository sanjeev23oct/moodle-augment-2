# Multi-Provider AI Chat API

A production-ready FastAPI application that provides a unified interface for multiple AI chat providers including OpenAI, Google Gemini, and Snowflake Cortex.

## Features

- **Multiple AI Providers**: Support for OpenAI GPT, Google Gemini, and Snowflake Cortex
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
cd python_ai_plugin

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
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
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

### OpenAI Chat
- **POST** `/chat/openai`
- Body: `{"prompt": "Your message here"}`

### Gemini Chat
- **POST** `/chat/gemini`
- Body: `{"prompt": "Your message here"}`

### Snowflake Cortex Chat
- **POST** `/chat/snowflake`
- Body: `{"prompt": "Your message here"}`

## API Documentation

Once running, visit:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Chat with OpenAI
response = requests.post(
    "http://localhost:8000/chat/openai",
    json={"prompt": "Hello, how are you?"}
)
print(response.json())
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | OpenAI API key |
| `GEMINI_API_KEY` | No | Google Gemini API key |
| `SNOWFLAKE_ACCOUNT` | No | Snowflake account identifier |
| `SNOWFLAKE_USER` | No | Snowflake username |
| `SNOWFLAKE_PASSWORD` | No | Snowflake password |
| `SNOWFLAKE_WAREHOUSE` | No | Snowflake warehouse name |
| `SNOWFLAKE_DATABASE` | No | Snowflake database name |
| `SNOWFLAKE_SCHEMA` | No | Snowflake schema name |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
| `CORS_ORIGINS` | No | CORS allowed origins (default: *) |

## Error Handling

The API returns structured error responses:

```json
{
  "error": "HTTP Error",
  "detail": "OpenAI API key not configured",
  "status_code": 503
}
```

## Logging

The application uses structured logging with configurable levels. Logs include:
- Request/response information
- API call details
- Error tracking
- Performance metrics

## Security Considerations

- API keys are loaded from environment variables
- No sensitive data is logged
- CORS is configurable for production use
- Input validation prevents injection attacks

## Production Deployment

For production deployment:

1. Use a production ASGI server like Gunicorn with Uvicorn workers
2. Set up proper environment variable management
3. Configure logging aggregation
4. Implement rate limiting
5. Set up monitoring and alerting

```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
