# AI-Powered Question Generator Plugin - Technical Specifications

## 1. Plugin Metadata

### 1.1 Basic Information
- **Plugin Name**: local_questiongen
- **Plugin Type**: Local plugin
- **Version**: 1.0.0
- **Moodle Version**: 4.0+
- **PHP Version**: 8.0+
- **Database**: PostgreSQL (primary), MySQL (compatible)

### 1.2 Dependencies
- Moodle core 4.0+
- cURL extension for API calls
- JSON extension for data processing
- OpenSSL for secure API communication

## 2. Database Schema

### 2.1 Table Definitions

#### 2.1.1 questiongen_sessions
```sql
CREATE TABLE mdl_questiongen_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES mdl_user(id),
    session_name VARCHAR(255) NOT NULL,
    content_text TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    ai_provider VARCHAR(50) DEFAULT 'openai',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_content_hash (content_hash),
    INDEX idx_created_at (created_at)
);
```

#### 2.1.2 questiongen_questions
```sql
CREATE TABLE mdl_questiongen_questions (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES mdl_questiongen_sessions(id) ON DELETE CASCADE,
    question_type VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    question_data JSON NOT NULL,
    is_ai_generated BOOLEAN DEFAULT TRUE,
    ai_confidence DECIMAL(3,2) DEFAULT NULL,
    created_by BIGINT NOT NULL REFERENCES mdl_user(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sort_order INTEGER DEFAULT 0,
    INDEX idx_session_id (session_id),
    INDEX idx_question_type (question_type),
    INDEX idx_created_by (created_by),
    INDEX idx_sort_order (sort_order)
);
```

#### 2.1.3 questiongen_ai_cache
```sql
CREATE TABLE mdl_questiongen_ai_cache (
    id BIGSERIAL PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    ai_provider VARCHAR(50) NOT NULL,
    ai_response JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    UNIQUE KEY unique_cache (content_hash, question_type, ai_provider),
    INDEX idx_expires_at (expires_at)
);
```

### 2.2 Question Data JSON Schema

#### 2.2.1 Multiple Choice Questions (MCQ)
```json
{
    "type": "mcq",
    "options": {
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
    },
    "correct_answer": "A",
    "explanation": "Optional explanation text",
    "difficulty": "medium",
    "tags": ["tag1", "tag2"]
}
```

#### 2.2.2 Short Answer Questions
```json
{
    "type": "short_answer",
    "correct_answer": "Expected answer text",
    "alternative_answers": ["Alternative 1", "Alternative 2"],
    "keywords": ["keyword1", "keyword2"],
    "case_sensitive": false,
    "difficulty": "easy",
    "tags": ["tag1", "tag2"]
}
```

#### 2.2.3 Fill in the Blanks
```json
{
    "type": "fill_blanks",
    "blanks": [
        {
            "position": 1,
            "correct_answer": "answer1",
            "alternatives": ["alt1", "alt2"]
        }
    ],
    "case_sensitive": false,
    "difficulty": "hard",
    "tags": ["tag1", "tag2"]
}
```

## 3. API Specifications

### 3.1 Internal Plugin APIs

#### 3.1.1 Question Generation Endpoint
```php
// URL: /local/questiongen/ajax/generate.php
// Method: POST
// Content-Type: application/json

Request:
{
    "content": "Chapter content text...",
    "question_type": "mcq|short_answer|fill_blanks",
    "count": 5,
    "difficulty": "easy|medium|hard",
    "session_name": "Optional session name"
}

Response:
{
    "success": true,
    "session_id": 123,
    "questions": [
        {
            "id": 456,
            "question_text": "What is...?",
            "question_data": {...},
            "ai_confidence": 0.95
        }
    ],
    "cache_hit": false
}
```

#### 3.1.2 Question Management Endpoints
```php
// Create Question: POST /local/questiongen/ajax/question.php
// Update Question: PUT /local/questiongen/ajax/question.php
// Delete Question: DELETE /local/questiongen/ajax/question.php?id=123
// Get Questions: GET /local/questiongen/ajax/questions.php?session_id=123
```

### 3.2 External AI API Integration

#### 3.2.1 OpenAI Integration
```php
// Endpoint: https://api.openai.com/v1/chat/completions
// Headers: Authorization: Bearer {api_key}

Request:
{
    "model": "gpt-4",
    "messages": [
        {
            "role": "system",
            "content": "You are a question generator..."
        },
        {
            "role": "user", 
            "content": "Generate 5 MCQ questions from: {content}"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 2000
}
```

#### 3.2.2 Anthropic Claude Integration
```php
// Endpoint: https://api.anthropic.com/v1/messages
// Headers: x-api-key: {api_key}

Request:
{
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 2000,
    "messages": [
        {
            "role": "user",
            "content": "Generate questions from content..."
        }
    ]
}
```

## 4. Class Specifications

### 4.1 Core Classes

#### 4.1.1 Question Generator Service
```php
namespace local_questiongen\service;

class question_generator {
    public function generate_questions(
        string $content,
        string $type,
        int $count = 5,
        array $options = []
    ): array;
    
    public function get_ai_provider(): ai_provider_interface;
    public function set_ai_provider(ai_provider_interface $provider): void;
    public function validate_content(string $content): bool;
}
```

#### 4.1.2 Question Manager
```php
namespace local_questiongen\manager;

class question_manager {
    public function create_question(array $data): int;
    public function update_question(int $id, array $data): bool;
    public function delete_question(int $id): bool;
    public function get_question(int $id): ?stdClass;
    public function get_questions_by_session(int $session_id): array;
    public function validate_question_data(array $data): array;
}
```

#### 4.1.3 Session Manager
```php
namespace local_questiongen\manager;

class session_manager {
    public function create_session(array $data): int;
    public function get_session(int $id): ?stdClass;
    public function get_user_sessions(int $user_id): array;
    public function delete_session(int $id): bool;
    public function update_session(int $id, array $data): bool;
}
```

### 4.2 AI Provider Interface
```php
namespace local_questiongen\ai;

interface ai_provider_interface {
    public function generate_questions(
        string $content,
        string $type,
        int $count,
        array $options = []
    ): array;
    
    public function validate_api_key(): bool;
    public function get_provider_name(): string;
    public function get_rate_limits(): array;
    public function format_prompt(string $content, string $type): string;
}
```

## 5. Configuration Specifications

### 5.1 Plugin Settings
```php
// settings.php configuration options
$settings->add(new admin_setting_configtext(
    'local_questiongen/openai_api_key',
    get_string('openai_api_key', 'local_questiongen'),
    get_string('openai_api_key_desc', 'local_questiongen'),
    '',
    PARAM_TEXT
));

$settings->add(new admin_setting_configselect(
    'local_questiongen/default_ai_provider',
    get_string('default_ai_provider', 'local_questiongen'),
    get_string('default_ai_provider_desc', 'local_questiongen'),
    'openai',
    ['openai' => 'OpenAI', 'anthropic' => 'Anthropic']
));
```

### 5.2 Capabilities
```php
// db/access.php
$capabilities = [
    'local/questiongen:generate' => [
        'captype' => 'write',
        'contextlevel' => CONTEXT_SYSTEM,
        'archetypes' => [
            'teacher' => CAP_ALLOW,
            'editingteacher' => CAP_ALLOW,
            'manager' => CAP_ALLOW
        ]
    ],
    'local/questiongen:manage' => [
        'captype' => 'write',
        'contextlevel' => CONTEXT_SYSTEM,
        'archetypes' => [
            'editingteacher' => CAP_ALLOW,
            'manager' => CAP_ALLOW
        ]
    ]
];
```

## 6. Frontend Specifications

### 6.1 JavaScript Modules (AMD)
```javascript
// amd/src/question_generator.js
define(['jquery', 'core/ajax', 'core/notification'], 
function($, Ajax, Notification) {
    return {
        init: function() {
            this.bindEvents();
        },
        
        generateQuestions: function(content, type, count) {
            return Ajax.call([{
                methodname: 'local_questiongen_generate_questions',
                args: {content: content, type: type, count: count}
            }])[0];
        },
        
        bindEvents: function() {
            $('#generate-btn').on('click', this.handleGenerate.bind(this));
        }
    };
});
```

### 6.2 Mustache Templates
```mustache
{{! templates/question_list.mustache }}
<div class="question-list">
    {{#questions}}
    <div class="question-item" data-id="{{id}}">
        <div class="question-header">
            <span class="question-type">{{type}}</span>
            <span class="question-number">{{@index}}</span>
        </div>
        <div class="question-content">
            <p class="question-text">{{question_text}}</p>
            {{#is_mcq}}
                {{>local_questiongen/mcq_options}}
            {{/is_mcq}}
        </div>
        <div class="question-actions">
            <button class="btn btn-secondary edit-question">Edit</button>
            <button class="btn btn-danger delete-question">Delete</button>
        </div>
    </div>
    {{/questions}}
</div>
```

## 7. Error Handling Specifications

### 7.1 Error Codes
- QG001: Invalid content format
- QG002: AI API connection failed
- QG003: AI API rate limit exceeded
- QG004: Invalid question type
- QG005: Database operation failed
- QG006: Insufficient permissions
- QG007: Session not found
- QG008: Question validation failed

### 7.2 Exception Classes
```php
namespace local_questiongen\exception;

class question_generation_exception extends \moodle_exception {}
class ai_api_exception extends \moodle_exception {}
class validation_exception extends \moodle_exception {}
```

## 8. Performance Specifications

### 8.1 Response Time Requirements
- Question generation: < 30 seconds
- Question CRUD operations: < 2 seconds
- Page load time: < 3 seconds
- AI API timeout: 60 seconds

### 8.2 Caching Strategy
- AI responses cached for 24 hours
- Database query caching enabled
- Static asset caching via Moodle's cache system
