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
 * Question Manager for AI Question Generator plugin.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_ai_question_gen\manager;

/**
 * Manages individual questions within sessions.
 */
class question_manager {
    
    /**
     * Create a new question.
     *
     * @param array $data Question data
     * @return int Question ID
     */
    public function create_question(array $data): int {
        global $DB, $USER;
        
        $record = new \stdClass();
        $record->session_id = $data['session_id'];
        $record->question_type = $data['question_type'];
        $record->question_text = $data['question_text'];
        $record->question_data = is_string($data['question_data']) ? 
            $data['question_data'] : json_encode($data['question_data']);
        $record->is_ai_generated = $data['is_ai_generated'] ?? 0;
        $record->ai_confidence = $data['ai_confidence'] ?? null;
        $record->difficulty = $data['difficulty'] ?? 'medium';
        $record->tags = $data['tags'] ?? '';
        $record->created_by = $USER->id;
        $record->created_at = time();
        $record->updated_at = time();
        $record->sort_order = $this->get_next_sort_order($data['session_id']);
        $record->status = 'active';
        
        return $DB->insert_record('ai_question_gen_questions', $record);
    }
    
    /**
     * Get a question by ID.
     *
     * @param int $id Question ID
     * @return \stdClass|null Question object or null if not found
     */
    public function get_question(int $id): ?\stdClass {
        global $DB;
        
        $question = $DB->get_record('ai_question_gen_questions', ['id' => $id, 'status' => 'active']);
        if ($question && $question->question_data) {
            $question->question_data = json_decode($question->question_data, true);
        }
        
        return $question;
    }
    
    /**
     * Get questions by session ID.
     *
     * @param int $session_id Session ID
     * @param string $sort_order Sort order (sort_order ASC, created_at DESC, etc.)
     * @return array Array of question objects
     */
    public function get_questions_by_session(int $session_id, string $sort_order = 'sort_order ASC'): array {
        global $DB;
        
        $questions = $DB->get_records('ai_question_gen_questions', 
            ['session_id' => $session_id, 'status' => 'active'], 
            $sort_order
        );
        
        // Decode JSON data for each question
        foreach ($questions as $question) {
            if ($question->question_data) {
                $question->question_data = json_decode($question->question_data, true);
            }
        }
        
        return $questions;
    }
    
    /**
     * Update a question.
     *
     * @param int $id Question ID
     * @param array $data Data to update
     * @return bool True on success
     */
    public function update_question(int $id, array $data): bool {
        global $DB;
        
        $record = new \stdClass();
        $record->id = $id;
        $record->updated_at = time();
        
        // Only update allowed fields
        $allowed_fields = ['question_text', 'question_data', 'difficulty', 'tags', 'sort_order'];
        foreach ($allowed_fields as $field) {
            if (isset($data[$field])) {
                if ($field === 'question_data' && is_array($data[$field])) {
                    $record->$field = json_encode($data[$field]);
                } else {
                    $record->$field = $data[$field];
                }
            }
        }
        
        return $DB->update_record('ai_question_gen_questions', $record);
    }
    
    /**
     * Delete a question (soft delete).
     *
     * @param int $id Question ID
     * @return bool True on success
     */
    public function delete_question(int $id): bool {
        global $DB;
        
        $record = new \stdClass();
        $record->id = $id;
        $record->status = 'deleted';
        $record->updated_at = time();
        
        return $DB->update_record('ai_question_gen_questions', $record);
    }
    
    /**
     * Bulk create questions from AI generation.
     *
     * @param int $session_id Session ID
     * @param array $questions Array of question data
     * @return array Array of created question IDs
     */
    public function bulk_create_questions(int $session_id, array $questions): array {
        global $DB;
        
        $question_ids = [];
        $transaction = $DB->start_delegated_transaction();
        
        try {
            foreach ($questions as $question_data) {
                $question_data['session_id'] = $session_id;
                $question_ids[] = $this->create_question($question_data);
            }
            
            $transaction->allow_commit();
            return $question_ids;
        } catch (\Exception $e) {
            $transaction->rollback($e);
            throw $e;
        }
    }
    
    /**
     * Reorder questions in a session.
     *
     * @param array $question_orders Array of question_id => sort_order
     * @return bool True on success
     */
    public function reorder_questions(array $question_orders): bool {
        global $DB;
        
        $transaction = $DB->start_delegated_transaction();
        
        try {
            foreach ($question_orders as $question_id => $sort_order) {
                $record = new \stdClass();
                $record->id = $question_id;
                $record->sort_order = $sort_order;
                $record->updated_at = time();
                
                $DB->update_record('ai_question_gen_questions', $record);
            }
            
            $transaction->allow_commit();
            return true;
        } catch (\Exception $e) {
            $transaction->rollback($e);
            return false;
        }
    }
    
    /**
     * Get next sort order for a session.
     *
     * @param int $session_id Session ID
     * @return int Next sort order
     */
    private function get_next_sort_order(int $session_id): int {
        global $DB;
        
        $max_order = $DB->get_field('ai_question_gen_questions', 
            'MAX(sort_order)', 
            ['session_id' => $session_id, 'status' => 'active']
        );
        
        return ($max_order ?? 0) + 1;
    }
    
    /**
     * Validate question data based on type.
     *
     * @param array $data Question data to validate
     * @return array Validation errors (empty if valid)
     */
    public function validate_question_data(array $data): array {
        $errors = [];
        
        // Basic validation
        if (empty($data['question_text'])) {
            $errors[] = 'Question text is required';
        }
        
        if (empty($data['question_type'])) {
            $errors[] = 'Question type is required';
        }
        
        // Type-specific validation
        switch ($data['question_type']) {
            case 'mcq':
                $errors = array_merge($errors, $this->validate_mcq_data($data));
                break;
            case 'short_answer':
                $errors = array_merge($errors, $this->validate_short_answer_data($data));
                break;
            case 'fill_blanks':
                $errors = array_merge($errors, $this->validate_fill_blanks_data($data));
                break;
            case 'truefalse':
                $errors = array_merge($errors, $this->validate_truefalse_data($data));
                break;
        }
        
        return $errors;
    }
    
    /**
     * Validate MCQ question data.
     */
    private function validate_mcq_data(array $data): array {
        $errors = [];
        $question_data = $data['question_data'] ?? [];
        
        if (empty($question_data['options']) || count($question_data['options']) < 2) {
            $errors[] = 'MCQ must have at least 2 options';
        }
        
        if (empty($question_data['correct_answer'])) {
            $errors[] = 'MCQ must have a correct answer';
        }
        
        return $errors;
    }
    
    /**
     * Validate short answer question data.
     */
    private function validate_short_answer_data(array $data): array {
        $errors = [];
        $question_data = $data['question_data'] ?? [];
        
        if (empty($question_data['correct_answer'])) {
            $errors[] = 'Short answer question must have a correct answer';
        }
        
        return $errors;
    }
    
    /**
     * Validate fill in the blanks question data.
     */
    private function validate_fill_blanks_data(array $data): array {
        $errors = [];
        $question_data = $data['question_data'] ?? [];
        
        if (empty($question_data['blanks']) || !is_array($question_data['blanks'])) {
            $errors[] = 'Fill in the blanks question must have blank definitions';
        }
        
        return $errors;
    }
    
    /**
     * Validate true/false question data.
     */
    private function validate_truefalse_data(array $data): array {
        $errors = [];
        $question_data = $data['question_data'] ?? [];
        
        if (!isset($question_data['correct_answer']) || 
            !in_array($question_data['correct_answer'], ['true', 'false'])) {
            $errors[] = 'True/false question must have correct answer as "true" or "false"';
        }
        
        return $errors;
    }
}
