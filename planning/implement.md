# AI-Powered Question Generator Plugin - Implementation Guide

## 1. Getting Started

### 1.1 Prerequisites
- Moodle 4.0+ development environment
- PHP 8.0+ with cURL and JSON extensions
- PostgreSQL or MySQL database
- Git for version control
- Code editor with PHP support

### 1.2 Initial Setup
```bash
# Navigate to Moodle local plugins directory
cd /path/to/moodle/local/

# Create plugin directory
mkdir questiongen
cd questiongen

# Initialize git repository
git init
```

## 2. Phase 1: Foundation Implementation

### 2.1 Plugin Structure Setup

#### Create version.php
```php
<?php
defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_questiongen';
$plugin->version = 2024091400;
$plugin->requires = 2022041900; // Moodle 4.0
$plugin->maturity = MATURITY_ALPHA;
$plugin->release = '1.0.0';
```

#### Create lib.php
```php
<?php
defined('MOODLE_INTERNAL') || die();

/**
 * Plugin navigation hook
 */
function local_questiongen_extend_navigation(global_navigation $navigation) {
    if (has_capability('local/questiongen:generate', context_system::instance())) {
        $node = $navigation->add(
            get_string('pluginname', 'local_questiongen'),
            new moodle_url('/local/questiongen/index.php'),
            navigation_node::TYPE_CUSTOM,
            null,
            'questiongen'
        );
        $node->showinflatnavigation = true;
    }
}
```

#### Create language file (lang/en/local_questiongen.php)
```php
<?php
$string['pluginname'] = 'AI Question Generator';
$string['questiongen:generate'] = 'Generate questions using AI';
$string['questiongen:manage'] = 'Manage generated questions';
$string['generatequestions'] = 'Generate Questions';
$string['contentinput'] = 'Chapter Content';
$string['questiontype'] = 'Question Type';
$string['mcq'] = 'Multiple Choice';
$string['shortanswer'] = 'Short Answer';
$string['fillblanks'] = 'Fill in the Blanks';
```

### 2.2 Database Schema Implementation

#### Create db/install.xml
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<XMLDB PATH="local/questiongen/db" VERSION="20240914" COMMENT="Question Generator Tables">
  <TABLES>
    <TABLE NAME="questiongen_sessions" COMMENT="Question generation sessions">
      <FIELDS>
        <FIELD NAME="id" TYPE="int" LENGTH="10" NOTNULL="true" SEQUENCE="true"/>
        <FIELD NAME="user_id" TYPE="int" LENGTH="10" NOTNULL="true"/>
        <FIELD NAME="session_name" TYPE="char" LENGTH="255" NOTNULL="true"/>
        <FIELD NAME="content_text" TYPE="text" NOTNULL="true"/>
        <FIELD NAME="content_hash" TYPE="char" LENGTH="64" NOTNULL="true"/>
        <FIELD NAME="question_type" TYPE="char" LENGTH="50" NOTNULL="true"/>
        <FIELD NAME="ai_provider" TYPE="char" LENGTH="50" NOTNULL="false" DEFAULT="openai"/>
        <FIELD NAME="created_at" TYPE="int" LENGTH="10" NOTNULL="true"/>
        <FIELD NAME="updated_at" TYPE="int" LENGTH="10" NOTNULL="true"/>
      </FIELDS>
      <KEYS>
        <KEY NAME="primary" TYPE="primary" FIELDS="id"/>
        <KEY NAME="user_id" TYPE="foreign" FIELDS="user_id" REFTABLE="user" REFFIELDS="id"/>
      </KEYS>
      <INDEXES>
        <INDEX NAME="content_hash" UNIQUE="false" FIELDS="content_hash"/>
        <INDEX NAME="created_at" UNIQUE="false" FIELDS="created_at"/>
      </INDEXES>
    </TABLE>
    
    <TABLE NAME="questiongen_questions" COMMENT="Generated questions">
      <FIELDS>
        <FIELD NAME="id" TYPE="int" LENGTH="10" NOTNULL="true" SEQUENCE="true"/>
        <FIELD NAME="session_id" TYPE="int" LENGTH="10" NOTNULL="true"/>
        <FIELD NAME="question_type" TYPE="char" LENGTH="50" NOTNULL="true"/>
        <FIELD NAME="question_text" TYPE="text" NOTNULL="true"/>
        <FIELD NAME="question_data" TYPE="text" NOTNULL="true"/>
        <FIELD NAME="is_ai_generated" TYPE="int" LENGTH="1" NOTNULL="true" DEFAULT="1"/>
        <FIELD NAME="ai_confidence" TYPE="number" LENGTH="3" DECIMALS="2" NOTNULL="false"/>
        <FIELD NAME="created_by" TYPE="int" LENGTH="10" NOTNULL="true"/>
        <FIELD NAME="created_at" TYPE="int" LENGTH="10" NOTNULL="true"/>
        <FIELD NAME="updated_at" TYPE="int" LENGTH="10" NOTNULL="true"/>
        <FIELD NAME="sort_order" TYPE="int" LENGTH="10" NOTNULL="true" DEFAULT="0"/>
      </FIELDS>
      <KEYS>
        <KEY NAME="primary" TYPE="primary" FIELDS="id"/>
        <KEY NAME="session_id" TYPE="foreign" FIELDS="session_id" REFTABLE="questiongen_sessions" REFFIELDS="id"/>
        <KEY NAME="created_by" TYPE="foreign" FIELDS="created_by" REFTABLE="user" REFFIELDS="id"/>
      </KEYS>
      <INDEXES>
        <INDEX NAME="question_type" UNIQUE="false" FIELDS="question_type"/>
        <INDEX NAME="sort_order" UNIQUE="false" FIELDS="sort_order"/>
      </INDEXES>
    </TABLE>
  </TABLES>
</XMLDB>
```

#### Create db/access.php
```php
<?php
defined('MOODLE_INTERNAL') || die();

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

## 3. Phase 2: Core Backend Development

### 3.1 AI Provider Interface

#### Create classes/ai/ai_provider_interface.php
```php
<?php
namespace local_questiongen\ai;

interface ai_provider_interface {
    /**
     * Generate questions from content
     */
    public function generate_questions(string $content, string $type, int $count, array $options = []): array;
    
    /**
     * Validate API configuration
     */
    public function validate_api_key(): bool;
    
    /**
     * Get provider name
     */
    public function get_provider_name(): string;
    
    /**
     * Format prompt for AI
     */
    public function format_prompt(string $content, string $type): string;
}
```

#### Create classes/ai/openai_provider.php
```php
<?php
namespace local_questiongen\ai;

class openai_provider implements ai_provider_interface {
    private $api_key;
    private $api_url = 'https://api.openai.com/v1/chat/completions';
    
    public function __construct() {
        $this->api_key = get_config('local_questiongen', 'openai_api_key');
    }
    
    public function generate_questions(string $content, string $type, int $count, array $options = []): array {
        $prompt = $this->format_prompt($content, $type);
        
        $data = [
            'model' => 'gpt-4',
            'messages' => [
                ['role' => 'system', 'content' => $this->get_system_prompt()],
                ['role' => 'user', 'content' => $prompt]
            ],
            'temperature' => 0.7,
            'max_tokens' => 2000
        ];
        
        $response = $this->make_api_call($data);
        return $this->parse_response($response, $type);
    }
    
    private function make_api_call(array $data): array {
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->api_url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($data),
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Authorization: Bearer ' . $this->api_key
            ],
            CURLOPT_TIMEOUT => 60
        ]);
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            throw new \moodle_exception('ai_api_error', 'local_questiongen', '', $http_code);
        }
        
        return json_decode($response, true);
    }
    
    public function format_prompt(string $content, string $type): string {
        $prompts = [
            'mcq' => "Generate 5 multiple choice questions from this content. Format as JSON with question, options A-D, and correct answer:\n\n{$content}",
            'short_answer' => "Generate 5 short answer questions from this content. Format as JSON with question and answer:\n\n{$content}",
            'fill_blanks' => "Generate 5 fill-in-the-blank questions from this content. Format as JSON with question (use ___ for blanks) and answers:\n\n{$content}"
        ];
        
        return $prompts[$type] ?? $prompts['mcq'];
    }
    
    // Additional methods...
}
```

### 3.2 Question Generation Service

#### Create classes/service/question_generator.php
```php
<?php
namespace local_questiongen\service;

use local_questiongen\ai\ai_provider_interface;
use local_questiongen\ai\openai_provider;

class question_generator {
    private $ai_provider;
    
    public function __construct(ai_provider_interface $provider = null) {
        $this->ai_provider = $provider ?: new openai_provider();
    }
    
    public function generate_questions(string $content, string $type, int $count = 5, array $options = []): array {
        // Validate input
        $this->validate_content($content);
        $this->validate_question_type($type);
        
        // Process content
        $processed_content = $this->process_content($content);
        
        // Generate questions using AI
        $ai_questions = $this->ai_provider->generate_questions($processed_content, $type, $count, $options);
        
        // Validate and format questions
        $formatted_questions = [];
        foreach ($ai_questions as $question) {
            if ($this->validate_question($question, $type)) {
                $formatted_questions[] = $this->format_question($question, $type);
            }
        }
        
        return $formatted_questions;
    }
    
    private function validate_content(string $content): void {
        if (empty(trim($content))) {
            throw new \invalid_parameter_exception('Content cannot be empty');
        }
        
        if (strlen($content) < 50) {
            throw new \invalid_parameter_exception('Content too short for question generation');
        }
        
        if (strlen($content) > 10000) {
            throw new \invalid_parameter_exception('Content too long, please split into smaller sections');
        }
    }
    
    private function validate_question_type(string $type): void {
        $valid_types = ['mcq', 'short_answer', 'fill_blanks'];
        if (!in_array($type, $valid_types)) {
            throw new \invalid_parameter_exception('Invalid question type: ' . $type);
        }
    }
    
    private function process_content(string $content): string {
        // Clean and prepare content for AI processing
        $content = strip_tags($content);
        $content = preg_replace('/\s+/', ' ', $content);
        $content = trim($content);
        
        return $content;
    }
    
    // Additional methods for validation and formatting...
}
```

## 4. Phase 3: Frontend Development

### 4.1 Main Interface (index.php)
```php
<?php
require_once('../../config.php');
require_login();

$context = context_system::instance();
require_capability('local/questiongen:generate', $context);

$PAGE->set_context($context);
$PAGE->set_url('/local/questiongen/index.php');
$PAGE->set_title(get_string('pluginname', 'local_questiongen'));
$PAGE->set_heading(get_string('pluginname', 'local_questiongen'));

// Include JavaScript
$PAGE->requires->js_call_amd('local_questiongen/question_generator', 'init');

echo $OUTPUT->header();

// Render main interface template
echo $OUTPUT->render_from_template('local_questiongen/main_interface', [
    'sesskey' => sesskey(),
    'question_types' => [
        ['value' => 'mcq', 'label' => get_string('mcq', 'local_questiongen')],
        ['value' => 'short_answer', 'label' => get_string('shortanswer', 'local_questiongen')],
        ['value' => 'fill_blanks', 'label' => get_string('fillblanks', 'local_questiongen')]
    ]
]);

echo $OUTPUT->footer();
```

### 4.2 Mustache Template (templates/main_interface.mustache)
```mustache
<div class="questiongen-container">
    <div class="content-input-section">
        <h3>{{#str}}contentinput, local_questiongen{{/str}}</h3>
        <form id="questiongen-form">
            <input type="hidden" name="sesskey" value="{{sesskey}}">
            
            <div class="form-group">
                <label for="content-text">{{#str}}contentinput, local_questiongen{{/str}}</label>
                <textarea id="content-text" name="content" rows="10" class="form-control" 
                         placeholder="Paste your chapter content here..." required></textarea>
            </div>
            
            <div class="form-group">
                <label>{{#str}}questiontype, local_questiongen{{/str}}</label>
                <div class="question-type-options">
                    {{#question_types}}
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="question_type" 
                               id="type-{{value}}" value="{{value}}" {{#@first}}checked{{/@first}}>
                        <label class="form-check-label" for="type-{{value}}">{{label}}</label>
                    </div>
                    {{/question_types}}
                </div>
            </div>
            
            <div class="form-group">
                <button type="submit" id="generate-btn" class="btn btn-primary">
                    {{#str}}generatequestions, local_questiongen{{/str}}
                </button>
                <div id="loading-indicator" class="d-none">
                    <i class="fa fa-spinner fa-spin"></i> Generating questions...
                </div>
            </div>
        </form>
    </div>
    
    <div id="questions-section" class="questions-section d-none">
        <h3>Generated Questions</h3>
        <div id="questions-list"></div>
    </div>
</div>
```

### 4.3 JavaScript Module (amd/src/question_generator.js)
```javascript
define(['jquery', 'core/ajax', 'core/notification'], function($, Ajax, Notification) {
    
    return {
        init: function() {
            this.bindEvents();
        },
        
        bindEvents: function() {
            $('#questiongen-form').on('submit', this.handleGenerate.bind(this));
            $(document).on('click', '.edit-question', this.handleEdit.bind(this));
            $(document).on('click', '.delete-question', this.handleDelete.bind(this));
        },
        
        handleGenerate: function(e) {
            e.preventDefault();
            
            var content = $('#content-text').val().trim();
            var questionType = $('input[name="question_type"]:checked').val();
            
            if (!content) {
                Notification.alert('Error', 'Please enter some content');
                return;
            }
            
            this.showLoading(true);
            
            Ajax.call([{
                methodname: 'local_questiongen_generate_questions',
                args: {
                    content: content,
                    question_type: questionType,
                    count: 5
                }
            }])[0].done(function(response) {
                this.showLoading(false);
                if (response.success) {
                    this.displayQuestions(response.questions);
                } else {
                    Notification.alert('Error', response.message || 'Failed to generate questions');
                }
            }.bind(this)).fail(function(error) {
                this.showLoading(false);
                Notification.alert('Error', 'Failed to generate questions: ' + error.message);
            }.bind(this));
        },
        
        showLoading: function(show) {
            if (show) {
                $('#generate-btn').prop('disabled', true);
                $('#loading-indicator').removeClass('d-none');
            } else {
                $('#generate-btn').prop('disabled', false);
                $('#loading-indicator').addClass('d-none');
            }
        },
        
        displayQuestions: function(questions) {
            var questionsHtml = '';
            questions.forEach(function(question, index) {
                questionsHtml += this.renderQuestion(question, index + 1);
            }.bind(this));
            
            $('#questions-list').html(questionsHtml);
            $('#questions-section').removeClass('d-none');
        },
        
        renderQuestion: function(question, number) {
            var html = '<div class="question-item card mb-3" data-id="' + question.id + '">';
            html += '<div class="card-header">';
            html += '<span class="question-number">' + number + '</span>';
            html += '<span class="question-type badge badge-info">' + question.type + '</span>';
            html += '<div class="question-actions float-right">';
            html += '<button class="btn btn-sm btn-secondary edit-question">Edit</button>';
            html += '<button class="btn btn-sm btn-danger delete-question ml-1">Delete</button>';
            html += '</div>';
            html += '</div>';
            html += '<div class="card-body">';
            html += '<p class="question-text">' + question.question_text + '</p>';
            
            if (question.type === 'mcq') {
                html += this.renderMCQOptions(question.question_data);
            }
            
            html += '</div>';
            html += '</div>';
            
            return html;
        },
        
        renderMCQOptions: function(data) {
            var html = '<div class="mcq-options">';
            Object.keys(data.options).forEach(function(key) {
                var isCorrect = key === data.correct_answer;
                var className = isCorrect ? 'list-group-item-success' : '';
                html += '<div class="list-group-item ' + className + '">';
                html += '<strong>' + key + ':</strong> ' + data.options[key];
                if (isCorrect) {
                    html += ' <i class="fa fa-check text-success"></i>';
                }
                html += '</div>';
            });
            html += '</div>';
            return html;
        }
    };
});
```

## 5. Testing Strategy

### 5.1 Unit Testing Example
```php
<?php
namespace local_questiongen;

class question_generator_test extends \advanced_testcase {
    
    public function setUp(): void {
        $this->resetAfterTest();
    }
    
    public function test_generate_mcq_questions() {
        // Mock AI provider
        $mock_provider = $this->createMock(\local_questiongen\ai\ai_provider_interface::class);
        $mock_provider->method('generate_questions')->willReturn([
            [
                'question_text' => 'What is PHP?',
                'options' => ['A' => 'Language', 'B' => 'Framework', 'C' => 'Database', 'D' => 'Server'],
                'correct_answer' => 'A'
            ]
        ]);
        
        $generator = new \local_questiongen\service\question_generator($mock_provider);
        $questions = $generator->generate_questions('PHP is a programming language', 'mcq', 1);
        
        $this->assertCount(1, $questions);
        $this->assertEquals('What is PHP?', $questions[0]['question_text']);
    }
}
```

## 6. Best Practices

### 6.1 Security Guidelines
- Always validate and sanitize user inputs
- Use Moodle's built-in security functions
- Implement proper capability checks
- Secure API key storage
- Prevent SQL injection with DML API

### 6.2 Performance Optimization
- Implement caching for AI responses
- Use database indexes effectively
- Optimize JavaScript loading
- Implement pagination for large datasets

### 6.3 Code Quality
- Follow Moodle coding standards
- Use proper namespacing
- Implement comprehensive error handling
- Write meaningful comments and documentation
- Use dependency injection for testability

## 7. Deployment Checklist

- [ ] All database tables created successfully
- [ ] Plugin capabilities working correctly
- [ ] AI integration functional with valid API keys
- [ ] Frontend interface responsive and accessible
- [ ] All unit tests passing
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Documentation updated
- [ ] User acceptance testing completed
