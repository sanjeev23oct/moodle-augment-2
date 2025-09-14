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
 * Main page for AI Question Generator plugin.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once('../../config.php');

// Check login and capabilities.
require_login();
$context = context_system::instance();
require_capability('local/ai_question_gen:generate', $context);

// Get parameters.
$session_id = optional_param('session_id', 0, PARAM_INT);
$action = optional_param('action', 'view', PARAM_ALPHA);

// Set up page.
$PAGE->set_context($context);
$PAGE->set_url('/local/ai_question_gen/index.php');
$PAGE->set_title(get_string('pluginname', 'local_ai_question_gen'));
$PAGE->set_heading(get_string('pluginname', 'local_ai_question_gen'));
$PAGE->set_pagelayout('standard');

// Include required JavaScript.
$PAGE->requires->js_call_amd('local_ai_question_gen/question_generator', 'init');
$PAGE->requires->css('/local/ai_question_gen/styles.css');

// Initialize managers.
$session_manager = new \local_ai_question_gen\manager\session_manager();
$question_manager = new \local_ai_question_gen\manager\question_manager();

// Handle actions.
$current_session = null;
$questions = [];

if ($session_id && $session_manager->can_access_session($session_id, $USER->id)) {
    $current_session = $session_manager->get_session($session_id);
    if ($current_session) {
        $questions = $question_manager->get_questions_by_session($session_id);
    }
}

// Prepare template data.
$template_data = [
    'sesskey' => sesskey(),
    'current_session' => $current_session,
    'questions' => array_values($questions),
    'question_types' => [
        ['value' => 'mcq', 'label' => get_string('mcq', 'local_ai_question_gen'), 'selected' => true],
        ['value' => 'short_answer', 'label' => get_string('shortanswer', 'local_ai_question_gen')],
        ['value' => 'fill_blanks', 'label' => get_string('fillblanks', 'local_ai_question_gen')],
        ['value' => 'truefalse', 'label' => get_string('truefalse', 'local_ai_question_gen')]
    ],
    'question_counts' => [
        ['value' => 1, 'label' => '1'],
        ['value' => 3, 'label' => '3'],
        ['value' => 5, 'label' => '5', 'selected' => true],
        ['value' => 7, 'label' => '7'],
        ['value' => 10, 'label' => '10']
    ],
    'user_sessions' => $session_manager->get_user_sessions($USER->id, 10),
    'can_manage' => has_capability('local/ai_question_gen:manage', $context),
    'can_export' => has_capability('local/ai_question_gen:export', $context)
];

// Add session statistics if we have a current session.
if ($current_session) {
    $template_data['session_stats'] = $session_manager->get_session_stats($session_id);
}

// Output page.
echo $OUTPUT->header();

// Show any notifications.
if ($session_id && !$current_session) {
    \core\notification::error(get_string('error:sessionnotfound', 'local_ai_question_gen'));
}

// Render main interface.
echo $OUTPUT->render_from_template('local_ai_question_gen/main_interface', $template_data);

echo $OUTPUT->footer();
