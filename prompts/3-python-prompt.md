You are an expert Python engineer who always follows production-grade best practices: clean modular architecture, async/await for I/O, type hints, multi-layered error handling, environment-based configuration using Pydantic Settings, structured logging, and comprehensive docstrings.

Write a complete Python script (`app.py`) for a FastAPI application that provides a unified API for multiple AI chat providers (OpenAI, Google Gemini, Snowflake Cortex) with the following endpoints:

- **GET /health**: Returns a JSON response with application status and provider availability.
- **POST /chat/openai**: Accepts a JSON body with a `"prompt"` field, validates input using Pydantic (with custom validators), and calls the OpenAI Chat API. API key and config must be loaded from environment variables.
- **POST /chat/gemini**: Same request schema, calls Google Gemini API. API key/config from environment variables.
- **POST /chat/snowflake**: Same request schema, calls Snowflake Cortex API. Credentials from environment variables.

**Requirements:**
- Use async context-managed HTTP clients for API calls.
- Implement multi-layered structured error handling (function, endpoint, and global levels) with consistent error response models.
- Use Pydantic models for all request/response schemas, including custom validators and extensible fields.
- Configure logging via environment variables, using structured formats.
- Support CORS with configurable origins.
- Organize code into clear sections: configuration, models, setup, helper functions, endpoints, error handlers.
- Ensure extensibility for adding new providers.
- Use uvicorn for running the app.
- Output only the complete `app.py` file.
- Additionally, provide a detailed code document explaining the implementation, architecture, design decisions, and best practices demonstrated in `app.py`.
- Write test cases for the application using pytest and fastapi.testclient.
- Also write a start script `run.py` to start the app using uvicorn.