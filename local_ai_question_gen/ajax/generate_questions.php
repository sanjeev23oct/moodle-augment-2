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
 * AJAX endpoint for generating questions.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define('AJAX_SCRIPT', true);

require_once('../../../config.php');

// Check login and capabilities.
require_login();
require_capability('local/ai_question_gen:generate', context_system::instance());

// Verify session key.
require_sesskey();

// Get POST data.
$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    $input = $_POST;
}

try {
    // Validate required parameters.
    $session_name = required_param_array('session_name', PARAM_TEXT, $input);
    $content = required_param_array('content', PARAM_RAW, $input);
    $question_type = required_param_array('question_type', PARAM_ALPHA, $input);
    $question_count = optional_param_array('question_count', 5, PARAM_INT, $input);
    $session_id = optional_param_array('session_id', 0, PARAM_INT, $input);
    
    // Initialize services.
    $session_manager = new \local_ai_question_gen\manager\session_manager();
    $question_manager = new \local_ai_question_gen\manager\question_manager();
    $question_generator = new \local_ai_question_gen\service\question_generator();
    
    // Create or update session.
    if ($session_id && $session_manager->can_access_session($session_id, $USER->id)) {
        // Update existing session.
        $session_data = [
            'session_name' => $session_name,
            'content_text' => $content,
            'question_type' => $question_type,
            'question_count' => $question_count
        ];
        $session_manager->update_session($session_id, $session_data);
        
        // Clear existing questions if regenerating.
        $existing_questions = $question_manager->get_questions_by_session($session_id);
        foreach ($existing_questions as $question) {
            $question_manager->delete_question($question->id);
        }
    } else {
        // Create new session.
        $session_data = [
            'session_name' => $session_name,
            'content_text' => $content,
            'question_type' => $question_type,
            'question_count' => $question_count
        ];
        $session_id = $session_manager->create_session($session_data);
    }
    
    // Generate questions.
    $generated_questions = $question_generator->generate_questions($content, $question_type, $question_count);
    
    // Save questions to database.
    $question_ids = [];
    foreach ($generated_questions as $question_data) {
        $question_data['session_id'] = $session_id;
        $question_ids[] = $question_manager->create_question($question_data);
    }
    
    // Return success response.
    $response = [
        'success' => true,
        'session_id' => $session_id,
        'question_ids' => $question_ids,
        'message' => get_string('questionsgenerated', 'local_ai_question_gen')
    ];
    
} catch (Exception $e) {
    // Return error response.
    $response = [
        'success' => false,
        'message' => $e->getMessage()
    ];
    
    // Log the error for debugging.
    debugging('AI Question Generation Error: ' . $e->getMessage(), DEBUG_DEVELOPER);
}

// Set content type and return JSON response.
header('Content-Type: application/json');
echo json_encode($response);
