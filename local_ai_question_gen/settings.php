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
 * Settings for AI Question Generator plugin.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $settings = new admin_settingpage('local_ai_question_gen', get_string('pluginname', 'local_ai_question_gen'));
    
    // AI Provider Settings.
    $settings->add(new admin_setting_heading(
        'local_ai_question_gen/ai_providers_heading',
        get_string('settings', 'local_ai_question_gen'),
        get_string('settings', 'local_ai_question_gen')
    ));
    
    // OpenAI API Key.
    $settings->add(new admin_setting_configpasswordunmask(
        'local_ai_question_gen/openai_api_key',
        get_string('openai_api_key', 'local_ai_question_gen'),
        get_string('openai_api_key_desc', 'local_ai_question_gen'),
        ''
    ));
    
    // Anthropic API Key.
    $settings->add(new admin_setting_configpasswordunmask(
        'local_ai_question_gen/anthropic_api_key',
        get_string('anthropic_api_key', 'local_ai_question_gen'),
        get_string('anthropic_api_key_desc', 'local_ai_question_gen'),
        ''
    ));
    
    // Default AI Provider.
    $providers = [
        'openai' => get_string('provider_openai', 'local_ai_question_gen'),
        'anthropic' => get_string('provider_anthropic', 'local_ai_question_gen')
    ];
    $settings->add(new admin_setting_configselect(
        'local_ai_question_gen/default_ai_provider',
        get_string('default_ai_provider', 'local_ai_question_gen'),
        get_string('default_ai_provider_desc', 'local_ai_question_gen'),
        'openai',
        $providers
    ));
    
    // Generation Settings.
    $settings->add(new admin_setting_heading(
        'local_ai_question_gen/generation_heading',
        'Generation Settings',
        'Configure question generation parameters'
    ));
    
    // Maximum Questions per Request.
    $settings->add(new admin_setting_configtext(
        'local_ai_question_gen/max_questions_per_request',
        get_string('max_questions_per_request', 'local_ai_question_gen'),
        get_string('max_questions_per_request_desc', 'local_ai_question_gen'),
        '10',
        PARAM_INT
    ));
    
    // Cache Duration.
    $settings->add(new admin_setting_configtext(
        'local_ai_question_gen/cache_duration',
        get_string('cache_duration', 'local_ai_question_gen'),
        get_string('cache_duration_desc', 'local_ai_question_gen'),
        '24',
        PARAM_INT
    ));
    
    // Maximum Content Length.
    $settings->add(new admin_setting_configtext(
        'local_ai_question_gen/max_content_length',
        'Maximum Content Length',
        'Maximum number of characters allowed in content input',
        '10000',
        PARAM_INT
    ));
    
    // Enable Debug Mode.
    $settings->add(new admin_setting_configcheckbox(
        'local_ai_question_gen/debug_mode',
        'Debug Mode',
        'Enable debug mode for troubleshooting (logs additional information)',
        0
    ));
    
    // Python Service Settings (for future integration).
    $settings->add(new admin_setting_heading(
        'local_ai_question_gen/python_service_heading',
        'Python Service Settings',
        'Configuration for external Python AI service (future feature)'
    ));
    
    // Python Service URL.
    $settings->add(new admin_setting_configtext(
        'local_ai_question_gen/python_service_url',
        'Python Service URL',
        'URL of the Python AI service endpoint',
        'http://localhost:8000',
        PARAM_URL
    ));
    
    // Python Service API Key.
    $settings->add(new admin_setting_configpasswordunmask(
        'local_ai_question_gen/python_service_api_key',
        'Python Service API Key',
        'API key for authenticating with the Python service',
        ''
    ));
    
    // Enable Python Service.
    $settings->add(new admin_setting_configcheckbox(
        'local_ai_question_gen/enable_python_service',
        'Enable Python Service',
        'Use external Python service instead of direct AI API calls',
        0
    ));
    
    $ADMIN->add('localplugins', $settings);
}
