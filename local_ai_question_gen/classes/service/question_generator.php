<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Question Generator Service for AI Question Generator plugin.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_ai_question_gen\service;

/**
 * Main service class for generating questions.
 */
class question_generator {
    
    /**
     * Generate questions from content.
     * For now, this will return mock data until Python service is integrated.
     *
     * @param string $content The content to generate questions from
     * @param string $type The type of questions to generate
     * @param int $count Number of questions to generate
     * @param array $options Additional options
     * @return array Array of generated questions
     */
    public function generate_questions(string $content, string $type, int $count = 5, array $options = []): array {
        // Validate input
        $this->validate_content($content);
        $this->validate_question_type($type);
        $this->validate_question_count($count);
        
        // For now, return mock data until Python service is ready
        return $this->generate_mock_questions($content, $type, $count);
    }
    
    /**
     * Validate content input.
     *
     * @param string $content Content to validate
     * @throws \invalid_parameter_exception If content is invalid
     */
    private function validate_content(string $content): void {
        if (empty(trim($content))) {
            throw new \invalid_parameter_exception(get_string('error:nocontent', 'local_ai_question_gen'));
        }
        
        if (strlen($content) < 50) {
            throw new \invalid_parameter_exception(get_string('error:contenttoshort', 'local_ai_question_gen'));
        }
        
        if (strlen($content) > 10000) {
            throw new \invalid_parameter_exception(get_string('error:contenttoolong', 'local_ai_question_gen'));
        }
    }
    
    /**
     * Validate question type.
     *
     * @param string $type Question type to validate
     * @throws \invalid_parameter_exception If type is invalid
     */
    private function validate_question_type(string $type): void {
        $valid_types = ['mcq', 'short_answer', 'fill_blanks', 'truefalse'];
        if (!in_array($type, $valid_types)) {
            throw new \invalid_parameter_exception(get_string('error:invalidquestiontype', 'local_ai_question_gen'));
        }
    }
    
    /**
     * Validate question count.
     *
     * @param int $count Question count to validate
     * @throws \invalid_parameter_exception If count is invalid
     */
    private function validate_question_count(int $count): void {
        if ($count < 1 || $count > 10) {
            throw new \invalid_parameter_exception('Question count must be between 1 and 10');
        }
    }
    
    /**
     * Generate mock questions for testing UI.
     * This will be replaced with actual AI service integration later.
     *
     * @param string $content Content to base questions on
     * @param string $type Question type
     * @param int $count Number of questions
     * @return array Mock questions
     */
    private function generate_mock_questions(string $content, string $type, int $count): array {
        $questions = [];
        
        for ($i = 1; $i <= $count; $i++) {
            switch ($type) {
                case 'mcq':
                    $questions[] = $this->create_mock_mcq($i, $content);
                    break;
                case 'short_answer':
                    $questions[] = $this->create_mock_short_answer($i, $content);
                    break;
                case 'fill_blanks':
                    $questions[] = $this->create_mock_fill_blanks($i, $content);
                    break;
                case 'truefalse':
                    $questions[] = $this->create_mock_truefalse($i, $content);
                    break;
            }
        }
        
        return $questions;
    }
    
    /**
     * Create mock MCQ question.
     */
    private function create_mock_mcq(int $number, string $content): array {
        return [
            'question_text' => "Sample MCQ Question {$number} based on the provided content?",
            'question_type' => 'mcq',
            'question_data' => [
                'options' => [
                    'A' => 'First option',
                    'B' => 'Second option', 
                    'C' => 'Third option',
                    'D' => 'Fourth option'
                ],
                'correct_answer' => 'A',
                'explanation' => 'This is the correct answer because...'
            ],
            'difficulty' => 'medium',
            'ai_confidence' => 0.85,
            'is_ai_generated' => true
        ];
    }
    
    /**
     * Create mock short answer question.
     */
    private function create_mock_short_answer(int $number, string $content): array {
        return [
            'question_text' => "Sample Short Answer Question {$number}: Explain the main concept from the content.",
            'question_type' => 'short_answer',
            'question_data' => [
                'correct_answer' => 'Sample answer based on content',
                'alternative_answers' => ['Alternative answer 1', 'Alternative answer 2'],
                'keywords' => ['keyword1', 'keyword2'],
                'case_sensitive' => false
            ],
            'difficulty' => 'medium',
            'ai_confidence' => 0.80,
            'is_ai_generated' => true
        ];
    }
    
    /**
     * Create mock fill in the blanks question.
     */
    private function create_mock_fill_blanks(int $number, string $content): array {
        return [
            'question_text' => "Sample Fill in the Blanks Question {$number}: The main concept is _____ and it relates to _____.",
            'question_type' => 'fill_blanks',
            'question_data' => [
                'blanks' => [
                    [
                        'position' => 1,
                        'correct_answer' => 'concept',
                        'alternatives' => ['idea', 'principle']
                    ],
                    [
                        'position' => 2,
                        'correct_answer' => 'topic',
                        'alternatives' => ['subject', 'theme']
                    ]
                ],
                'case_sensitive' => false
            ],
            'difficulty' => 'easy',
            'ai_confidence' => 0.90,
            'is_ai_generated' => true
        ];
    }
    
    /**
     * Create mock true/false question.
     */
    private function create_mock_truefalse(int $number, string $content): array {
        return [
            'question_text' => "Sample True/False Question {$number}: The content discusses important concepts.",
            'question_type' => 'truefalse',
            'question_data' => [
                'correct_answer' => 'true',
                'explanation' => 'This statement is true because the content covers key concepts.'
            ],
            'difficulty' => 'easy',
            'ai_confidence' => 0.95,
            'is_ai_generated' => true
        ];
    }
}
