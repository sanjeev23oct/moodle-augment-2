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
 * English language strings for AI Question Generator plugin.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

// Plugin information.
$string['pluginname'] = 'AI Question Generator';
$string['ai_question_gen'] = 'AI Question Generator';

// Capabilities.
$string['ai_question_gen:generate'] = 'Generate questions using AI';
$string['ai_question_gen:manage'] = 'Manage generated questions';
$string['ai_question_gen:viewall'] = 'View all question sessions';

// Main interface.
$string['generatequestions'] = 'Generate Questions';
$string['contentinput'] = 'Chapter Content';
$string['contentinput_help'] = 'Paste or type the chapter content from which you want to generate questions. The content should be at least 50 characters long.';
$string['questiontype'] = 'Question Type';
$string['questiontype_help'] = 'Select the type of questions you want to generate from the content.';
$string['questioncount'] = 'Number of Questions';
$string['questioncount_help'] = 'Choose how many questions to generate (1-10).';

// Question types.
$string['mcq'] = 'Multiple Choice Questions';
$string['shortanswer'] = 'Short Answer Questions';
$string['fillblanks'] = 'Fill in the Blanks';
$string['truefalse'] = 'True/False Questions';

// Interface elements.
$string['generate'] = 'Generate';
$string['regenerate'] = 'Regenerate';
$string['addmanual'] = 'Add Manual Question';
$string['edit'] = 'Edit';
$string['delete'] = 'Delete';
$string['save'] = 'Save';
$string['cancel'] = 'Cancel';
$string['loading'] = 'Generating questions...';
$string['sessionname'] = 'Session Name';
$string['sessionname_help'] = 'Give this question session a name for easy identification.';

// Question management.
$string['questiontext'] = 'Question Text';
$string['questionoptions'] = 'Answer Options';
$string['correctanswer'] = 'Correct Answer';
$string['explanation'] = 'Explanation';
$string['difficulty'] = 'Difficulty';
$string['tags'] = 'Tags';
$string['aiconfidence'] = 'AI Confidence';

// Difficulty levels.
$string['difficulty_easy'] = 'Easy';
$string['difficulty_medium'] = 'Medium';
$string['difficulty_hard'] = 'Hard';

// Messages and notifications.
$string['questionsgenerated'] = 'Questions generated successfully!';
$string['questionssaved'] = 'Questions saved successfully!';
$string['questiondeleted'] = 'Question deleted successfully!';
$string['sessionsaved'] = 'Session saved successfully!';
$string['sessionloaded'] = 'Session loaded successfully!';

// Errors.
$string['error:nocontent'] = 'Please enter some content to generate questions from.';
$string['error:contenttoshort'] = 'Content is too short. Please provide at least 50 characters.';
$string['error:contenttoolong'] = 'Content is too long. Please limit to 10,000 characters.';
$string['error:invalidquestiontype'] = 'Invalid question type selected.';
$string['error:apikeynotset'] = 'AI API key is not configured. Please contact your administrator.';
$string['error:apierror'] = 'Error communicating with AI service: {$a}';
$string['error:nopermission'] = 'You do not have permission to perform this action.';
$string['error:sessionnotfound'] = 'Question session not found.';
$string['error:questionnotfound'] = 'Question not found.';
$string['error:invaliddata'] = 'Invalid data provided.';

// Settings.
$string['settings'] = 'AI Question Generator Settings';
$string['openai_api_key'] = 'OpenAI API Key';
$string['openai_api_key_desc'] = 'Enter your OpenAI API key to enable question generation using GPT models.';
$string['anthropic_api_key'] = 'Anthropic API Key';
$string['anthropic_api_key_desc'] = 'Enter your Anthropic API key to enable question generation using Claude models.';
$string['default_ai_provider'] = 'Default AI Provider';
$string['default_ai_provider_desc'] = 'Select the default AI provider for question generation.';
$string['max_questions_per_request'] = 'Maximum Questions per Request';
$string['max_questions_per_request_desc'] = 'Maximum number of questions that can be generated in a single request.';
$string['cache_duration'] = 'Cache Duration (hours)';
$string['cache_duration_desc'] = 'How long to cache AI responses to reduce API calls.';

// AI Providers.
$string['provider_openai'] = 'OpenAI (GPT)';
$string['provider_anthropic'] = 'Anthropic (Claude)';

// Privacy.
$string['privacy:metadata'] = 'The AI Question Generator plugin stores question generation sessions and generated questions.';
$string['privacy:metadata:questiongen_sessions'] = 'Information about question generation sessions.';
$string['privacy:metadata:questiongen_sessions:user_id'] = 'The ID of the user who created the session.';
$string['privacy:metadata:questiongen_sessions:session_name'] = 'The name given to the session.';
$string['privacy:metadata:questiongen_sessions:content_text'] = 'The content used to generate questions.';
$string['privacy:metadata:questiongen_sessions:created_at'] = 'The time when the session was created.';
$string['privacy:metadata:questiongen_questions'] = 'Information about generated questions.';
$string['privacy:metadata:questiongen_questions:question_text'] = 'The text of the generated question.';
$string['privacy:metadata:questiongen_questions:question_data'] = 'Additional data about the question (options, answers, etc.).';
$string['privacy:metadata:questiongen_questions:created_by'] = 'The ID of the user who created the question.';
$string['privacy:metadata:questiongen_questions:created_at'] = 'The time when the question was created.';

// External services.
$string['privacy:metadata:openai'] = 'The AI Question Generator plugin sends content to OpenAI to generate questions.';
$string['privacy:metadata:openai:content'] = 'The chapter content is sent to OpenAI for question generation.';
$string['privacy:metadata:anthropic'] = 'The AI Question Generator plugin sends content to Anthropic to generate questions.';
$string['privacy:metadata:anthropic:content'] = 'The chapter content is sent to Anthropic for question generation.';

// Tables and lists.
$string['nosessions'] = 'No question sessions found.';
$string['noquestions'] = 'No questions found in this session.';
$string['questionslist'] = 'Questions List';
$string['sessionslist'] = 'Sessions List';
$string['type'] = 'Type';
$string['question'] = 'Question';
$string['answer'] = 'Answer';
$string['actions'] = 'Actions';
$string['created'] = 'Created';
$string['modified'] = 'Modified';

// Buttons and links.
$string['newsession'] = 'New Session';
$string['loadsession'] = 'Load Session';
$string['deletesession'] = 'Delete Session';
$string['exportsession'] = 'Export Session';
$string['duplicatesession'] = 'Duplicate Session';

// Confirmations.
$string['confirmdelete'] = 'Are you sure you want to delete this item?';
$string['confirmdeletesession'] = 'Are you sure you want to delete this session and all its questions?';
$string['confirmregenerate'] = 'Are you sure you want to regenerate questions? This will replace existing questions.';

// Help texts.
$string['help:mcq'] = 'Multiple choice questions with 4 options (A, B, C, D) and one correct answer.';
$string['help:shortanswer'] = 'Questions that require a brief written response.';
$string['help:fillblanks'] = 'Questions with missing words that need to be filled in.';
$string['help:truefalse'] = 'Questions with only two possible answers: True or False.';
