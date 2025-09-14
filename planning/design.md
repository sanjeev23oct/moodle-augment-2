# AI-Powered Question Generator Plugin - Design Document

## 1. Overview

### 1.1 Project Description
An AI-powered Moodle plugin that enables teachers and content creators to automatically generate, manage, and customize questions based on chapter content. The plugin supports multiple question types and provides both AI-generated and manual question creation capabilities.

### 1.2 Target Users
- Teachers and educators
- Content creators
- Corporate trainers
- Educational administrators

## 2. System Architecture

### 2.1 High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Moodle UI     │    │   Plugin Core   │    │   AI Service   │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   Database      │    │   OpenAI/       │
│   (Mustache)    │    │   (Postgres)    │    │   Anthropic     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 Plugin Structure
Following Moodle's local plugin architecture:
- **local_questiongen/** - Main plugin directory
- **classes/** - Core PHP classes and business logic
- **templates/** - Mustache templates for UI
- **amd/** - JavaScript modules for frontend interaction
- **db/** - Database schema and upgrade scripts
- **lang/** - Localization files

## 3. User Interface Design

### 3.1 Main Interface Layout
```
┌─────────────────────────────────────────────────────────────┐
│                    Question Generator                        │
├─────────────────────────────────────────────────────────────┤
│ Content Input                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Paste chapter content here...]                         │ │
│ │                                                         │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Question Type: [MCQ ▼] [Short Answer] [Fill in Blanks]     │
│                                                             │
│ [Generate Questions] [Add Manual Question]                  │
├─────────────────────────────────────────────────────────────┤
│ Generated Questions                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ # | Type | Question | Answer | Actions                  │ │
│ │ 1 | MCQ  | What is...? | A | [Edit] [Delete]           │ │
│ │ 2 | SA   | Explain...  | ... | [Edit] [Delete]         │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Question Types Interface

#### 3.2.1 Multiple Choice Questions (MCQ)
- Question text field
- 4 option fields (A, B, C, D)
- Correct answer selection
- Explanation field (optional)

#### 3.2.2 Short Answer Questions
- Question text field
- Answer text field
- Keywords for partial matching (optional)

#### 3.2.3 Fill in the Blanks
- Question text with blank markers
- Correct answer(s) field
- Alternative answers (optional)

## 4. Technical Design

### 4.1 Core Components

#### 4.1.1 Question Generator Service
- **Purpose**: Interface with AI services to generate questions
- **Responsibilities**:
  - Format content for AI processing
  - Send requests to AI APIs
  - Parse and validate AI responses
  - Handle API errors and retries

#### 4.1.2 Question Manager
- **Purpose**: Manage question CRUD operations
- **Responsibilities**:
  - Create, read, update, delete questions
  - Validate question data
  - Handle question type-specific logic

#### 4.1.3 Content Processor
- **Purpose**: Process and prepare input content
- **Responsibilities**:
  - Clean and format text input
  - Extract key concepts and topics
  - Prepare content for AI consumption

### 4.2 Database Design

#### 4.2.1 Tables Structure
```sql
-- Main questions table
questiongen_questions
├── id (bigint, primary key)
├── content_hash (varchar, index)
├── question_type (varchar)
├── question_text (text)
├── question_data (json)
├── created_by (bigint, foreign key to users)
├── created_at (timestamp)
├── updated_at (timestamp)
└── is_ai_generated (boolean)

-- Question sessions for grouping
questiongen_sessions
├── id (bigint, primary key)
├── user_id (bigint, foreign key to users)
├── content_text (text)
├── content_hash (varchar, index)
├── session_name (varchar)
├── created_at (timestamp)
└── updated_at (timestamp)

-- Link questions to sessions
questiongen_session_questions
├── id (bigint, primary key)
├── session_id (bigint, foreign key)
├── question_id (bigint, foreign key)
└── sort_order (int)
```

### 4.3 AI Integration Design

#### 4.3.1 AI Service Interface
```php
interface AIQuestionGenerator {
    public function generateQuestions(
        string $content, 
        string $questionType, 
        int $count = 5
    ): array;
    
    public function validateResponse(array $response): bool;
    public function formatQuestions(array $aiResponse): array;
}
```

#### 4.3.2 Supported AI Providers
- OpenAI GPT-4/3.5
- Anthropic Claude
- Local LLM integration (future)

## 5. Security Considerations

### 5.1 Data Protection
- Sanitize all user inputs
- Validate AI responses before storage
- Implement rate limiting for AI API calls
- Secure API key storage in Moodle config

### 5.2 Access Control
- Leverage Moodle's capability system
- Role-based permissions for question generation
- User isolation for question sessions

### 5.3 Content Security
- Content validation and filtering
- Prevention of malicious prompt injection
- Audit logging for AI interactions

## 6. Performance Considerations

### 6.1 Optimization Strategies
- Caching of AI responses for similar content
- Asynchronous processing for large content
- Database indexing on frequently queried fields
- Pagination for question lists

### 6.2 Scalability
- Queue system for AI processing
- Connection pooling for database
- CDN integration for static assets

## 7. Integration Points

### 7.1 Moodle Integration
- Question bank integration
- Course context awareness
- User management integration
- Theme compatibility

### 7.2 External Services
- AI API integration
- Future: LTI compatibility
- Future: Export to external formats

## 8. Future Enhancements

### 8.1 Phase 2 Features
- PDF/DOCX file upload support
- Bulk question import/export
- Question difficulty assessment
- Learning analytics integration

### 8.2 Advanced Features
- Multi-language support
- Question templates
- Collaborative question creation
- Integration with question banks
