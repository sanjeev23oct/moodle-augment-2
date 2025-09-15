Based on the requirements.md file in this repository, create a Python-based question generator application with the following specifications:

**Core Functionality:**
- Create a question generator service that can process PDF files and generate educational questions
- Support multiple question types: multiple choice questions (MCQ) and short answer questions
- Generate questions based on content extracted from uploaded PDF files

**API Endpoints:**
- Implement two distinct endpoints:
  1. `/generate-questions/snowflake` - Uses Snowflake Cortex AI API for question generation
  2. `/generate-questions/deepseek` - Uses DeepSeek AI API for question generation
- Both endpoints should accept PDF file uploads and return generated questions in a structured format

**Technical Requirements:**
- Follow the same architectural patterns as the existing Python AI agent in this repository
- Ensure the application adheres to all specifications outlined in requirements.md
- Implement proper error handling, logging, and input validation
- Include appropriate API documentation and response schemas

**Deployment Configuration:**
- Update the existing `build_and_push.bat` script to include build and deployment steps for this new Python question generator application
- Ensure the batch script can handle both the existing services and the new question generator service
- Maintain compatibility with the current deployment pipeline

**Deliverables:**
1. Complete Python application code for the question generator service
2. Updated `build_and_push.bat` script with support for the new application
3. Any necessary configuration files, requirements.txt, or Docker files
4. Documentation for the new endpoints and their usage

Please first examine the requirements.md file and existing Python AI agent structure to understand the current patterns and requirements before implementing the solution.