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
 * Session Manager for AI Question Generator plugin.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_ai_question_gen\manager;

/**
 * Manages question generation sessions.
 */
class session_manager {
    
    /**
     * Create a new question generation session.
     *
     * @param array $data Session data
     * @return int Session ID
     */
    public function create_session(array $data): int {
        global $DB, $USER;
        
        $record = new \stdClass();
        $record->user_id = $USER->id;
        $record->session_name = $data['session_name'] ?? 'Untitled Session';
        $record->content_text = $data['content_text'];
        $record->content_hash = hash('sha256', $data['content_text']);
        $record->question_type = $data['question_type'];
        $record->question_count = $data['question_count'] ?? 5;
        $record->ai_provider = $data['ai_provider'] ?? 'openai';
        $record->status = 'active';
        $record->created_at = time();
        $record->updated_at = time();
        
        return $DB->insert_record('ai_question_gen_sessions', $record);
    }
    
    /**
     * Get a session by ID.
     *
     * @param int $id Session ID
     * @return \stdClass|null Session object or null if not found
     */
    public function get_session(int $id): ?\stdClass {
        global $DB;
        
        return $DB->get_record('ai_question_gen_sessions', ['id' => $id]);
    }
    
    /**
     * Get sessions for a user.
     *
     * @param int $user_id User ID
     * @param int $limit Limit number of results
     * @param int $offset Offset for pagination
     * @return array Array of session objects
     */
    public function get_user_sessions(int $user_id, int $limit = 50, int $offset = 0): array {
        global $DB;
        
        return $DB->get_records('ai_question_gen_sessions', 
            ['user_id' => $user_id, 'status' => 'active'], 
            'updated_at DESC', 
            '*', 
            $offset, 
            $limit
        );
    }
    
    /**
     * Update a session.
     *
     * @param int $id Session ID
     * @param array $data Data to update
     * @return bool True on success
     */
    public function update_session(int $id, array $data): bool {
        global $DB;
        
        $record = new \stdClass();
        $record->id = $id;
        $record->updated_at = time();
        
        // Only update allowed fields
        $allowed_fields = ['session_name', 'content_text', 'question_type', 'question_count', 'status'];
        foreach ($allowed_fields as $field) {
            if (isset($data[$field])) {
                $record->$field = $data[$field];
            }
        }
        
        // Update content hash if content changed
        if (isset($data['content_text'])) {
            $record->content_hash = hash('sha256', $data['content_text']);
        }
        
        return $DB->update_record('ai_question_gen_sessions', $record);
    }
    
    /**
     * Delete a session and all its questions.
     *
     * @param int $id Session ID
     * @return bool True on success
     */
    public function delete_session(int $id): bool {
        global $DB;
        
        // Start transaction
        $transaction = $DB->start_delegated_transaction();
        
        try {
            // Delete all questions in this session
            $DB->delete_records('ai_question_gen_questions', ['session_id' => $id]);
            
            // Delete the session
            $DB->delete_records('ai_question_gen_sessions', ['id' => $id]);
            
            $transaction->allow_commit();
            return true;
        } catch (\Exception $e) {
            $transaction->rollback($e);
            return false;
        }
    }
    
    /**
     * Check if user can access session.
     *
     * @param int $session_id Session ID
     * @param int $user_id User ID
     * @return bool True if user can access
     */
    public function can_access_session(int $session_id, int $user_id): bool {
        global $DB;
        
        // Check if user owns the session
        $session = $DB->get_record('ai_question_gen_sessions', ['id' => $session_id]);
        if (!$session) {
            return false;
        }
        
        // Owner can always access
        if ($session->user_id == $user_id) {
            return true;
        }
        
        // Check if user has viewall capability
        return has_capability('local/ai_question_gen:viewall', \context_system::instance(), $user_id);
    }
    
    /**
     * Get session statistics.
     *
     * @param int $session_id Session ID
     * @return array Statistics array
     */
    public function get_session_stats(int $session_id): array {
        global $DB;
        
        $sql = "SELECT 
                    COUNT(*) as total_questions,
                    SUM(CASE WHEN is_ai_generated = 1 THEN 1 ELSE 0 END) as ai_generated,
                    SUM(CASE WHEN is_ai_generated = 0 THEN 1 ELSE 0 END) as manual_created,
                    AVG(ai_confidence) as avg_confidence
                FROM {ai_question_gen_questions} 
                WHERE session_id = ? AND status = 'active'";
        
        $stats = $DB->get_record_sql($sql, [$session_id]);
        
        return [
            'total_questions' => (int)$stats->total_questions,
            'ai_generated' => (int)$stats->ai_generated,
            'manual_created' => (int)$stats->manual_created,
            'avg_confidence' => round((float)$stats->avg_confidence, 2)
        ];
    }
    
    /**
     * Duplicate a session.
     *
     * @param int $session_id Session ID to duplicate
     * @param string $new_name New session name
     * @return int New session ID
     */
    public function duplicate_session(int $session_id, string $new_name): int {
        global $DB;
        
        $original_session = $this->get_session($session_id);
        if (!$original_session) {
            throw new \moodle_exception('sessionnotfound', 'local_ai_question_gen');
        }
        
        // Create new session
        $new_session_data = [
            'session_name' => $new_name,
            'content_text' => $original_session->content_text,
            'question_type' => $original_session->question_type,
            'question_count' => $original_session->question_count,
            'ai_provider' => $original_session->ai_provider
        ];
        
        $new_session_id = $this->create_session($new_session_data);
        
        // Copy questions
        $question_manager = new \local_ai_question_gen\manager\question_manager();
        $questions = $question_manager->get_questions_by_session($session_id);
        
        foreach ($questions as $question) {
            $question_data = [
                'session_id' => $new_session_id,
                'question_type' => $question->question_type,
                'question_text' => $question->question_text,
                'question_data' => $question->question_data,
                'is_ai_generated' => $question->is_ai_generated,
                'ai_confidence' => $question->ai_confidence,
                'difficulty' => $question->difficulty,
                'tags' => $question->tags
            ];
            $question_manager->create_question($question_data);
        }
        
        return $new_session_id;
    }
}
