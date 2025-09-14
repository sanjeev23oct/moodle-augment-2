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
 * AI Question Generator plugin upgrade script.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Upgrade function for the AI Question Generator plugin.
 *
 * @param int $oldversion The old version of the plugin
 * @return bool True on success
 */
function xmldb_local_ai_question_gen_upgrade($oldversion) {
    global $DB;

    $dbman = $DB->get_manager();

    // Moodle v4.3.0 release upgrade line.
    // Put any upgrade step following this.

    if ($oldversion < 2024091401) {
        // Add new fields to sessions table if needed.
        $table = new xmldb_table('ai_question_gen_sessions');
        
        // Add question_count field if it doesn't exist.
        $field = new xmldb_field('question_count', XMLDB_TYPE_INTEGER, '3', null, XMLDB_NOTNULL, null, '5');
        if (!$dbman->field_exists($table, $field)) {
            $dbman->add_field($table, $field);
        }
        
        // Add status field if it doesn't exist.
        $field = new xmldb_field('status', XMLDB_TYPE_CHAR, '20', null, XMLDB_NOTNULL, null, 'active');
        if (!$dbman->field_exists($table, $field)) {
            $dbman->add_field($table, $field);
        }

        // AI Question Generator savepoint reached.
        upgrade_plugin_savepoint(true, 2024091401, 'local', 'ai_question_gen');
    }

    if ($oldversion < 2024091402) {
        // Add new fields to questions table if needed.
        $table = new xmldb_table('ai_question_gen_questions');
        
        // Add difficulty field if it doesn't exist.
        $field = new xmldb_field('difficulty', XMLDB_TYPE_CHAR, '20', null, null, null, 'medium');
        if (!$dbman->field_exists($table, $field)) {
            $dbman->add_field($table, $field);
        }
        
        // Add tags field if it doesn't exist.
        $field = new xmldb_field('tags', XMLDB_TYPE_TEXT, null, null, null, null, null);
        if (!$dbman->field_exists($table, $field)) {
            $dbman->add_field($table, $field);
        }
        
        // Add status field if it doesn't exist.
        $field = new xmldb_field('status', XMLDB_TYPE_CHAR, '20', null, XMLDB_NOTNULL, null, 'active');
        if (!$dbman->field_exists($table, $field)) {
            $dbman->add_field($table, $field);
        }

        // AI Question Generator savepoint reached.
        upgrade_plugin_savepoint(true, 2024091402, 'local', 'ai_question_gen');
    }

    if ($oldversion < 2024091403) {
        // Create cache table if it doesn't exist.
        $table = new xmldb_table('ai_question_gen_cache');
        if (!$dbman->table_exists($table)) {
            $table->add_field('id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, XMLDB_SEQUENCE, null);
            $table->add_field('content_hash', XMLDB_TYPE_CHAR, '64', null, XMLDB_NOTNULL, null, null);
            $table->add_field('question_type', XMLDB_TYPE_CHAR, '50', null, XMLDB_NOTNULL, null, null);
            $table->add_field('question_count', XMLDB_TYPE_INTEGER, '3', null, XMLDB_NOTNULL, null, null);
            $table->add_field('ai_provider', XMLDB_TYPE_CHAR, '50', null, XMLDB_NOTNULL, null, null);
            $table->add_field('ai_response', XMLDB_TYPE_TEXT, null, null, XMLDB_NOTNULL, null, null);
            $table->add_field('created_at', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
            $table->add_field('expires_at', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
            $table->add_field('hit_count', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, '0');

            $table->add_key('primary', XMLDB_KEY_PRIMARY, ['id']);
            $table->add_index('content_hash_type_provider', XMLDB_INDEX_UNIQUE, 
                ['content_hash', 'question_type', 'question_count', 'ai_provider']);
            $table->add_index('expires_at', XMLDB_INDEX_NOTUNIQUE, ['expires_at']);
            $table->add_index('created_at', XMLDB_INDEX_NOTUNIQUE, ['created_at']);

            $dbman->create_table($table);
        }

        // AI Question Generator savepoint reached.
        upgrade_plugin_savepoint(true, 2024091403, 'local', 'ai_question_gen');
    }

    if ($oldversion < 2024091404) {
        // Create exports table if it doesn't exist.
        $table = new xmldb_table('ai_question_gen_exports');
        if (!$dbman->table_exists($table)) {
            $table->add_field('id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, XMLDB_SEQUENCE, null);
            $table->add_field('session_id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
            $table->add_field('user_id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
            $table->add_field('export_format', XMLDB_TYPE_CHAR, '20', null, XMLDB_NOTNULL, null, null);
            $table->add_field('file_path', XMLDB_TYPE_CHAR, '500', null, null, null, null);
            $table->add_field('question_count', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
            $table->add_field('created_at', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, null, null);
            $table->add_field('status', XMLDB_TYPE_CHAR, '20', null, XMLDB_NOTNULL, null, 'completed');

            $table->add_key('primary', XMLDB_KEY_PRIMARY, ['id']);
            $table->add_key('session_id', XMLDB_KEY_FOREIGN, ['session_id'], 'ai_question_gen_sessions', ['id']);
            $table->add_key('user_id', XMLDB_KEY_FOREIGN, ['user_id'], 'user', ['id']);
            $table->add_index('created_at', XMLDB_INDEX_NOTUNIQUE, ['created_at']);
            $table->add_index('export_format', XMLDB_INDEX_NOTUNIQUE, ['export_format']);
            $table->add_index('status', XMLDB_INDEX_NOTUNIQUE, ['status']);

            $dbman->create_table($table);
        }

        // AI Question Generator savepoint reached.
        upgrade_plugin_savepoint(true, 2024091404, 'local', 'ai_question_gen');
    }

    // Clean up expired cache entries.
    if ($oldversion < 2024091405) {
        // Add a scheduled task to clean up expired cache entries.
        $DB->delete_records_select('ai_question_gen_cache', 'expires_at < ?', [time()]);

        // AI Question Generator savepoint reached.
        upgrade_plugin_savepoint(true, 2024091405, 'local', 'ai_question_gen');
    }

    return true;
}
