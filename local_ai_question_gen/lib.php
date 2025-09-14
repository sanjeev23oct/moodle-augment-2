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
 * AI Question Generator plugin library functions.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Extend the global navigation tree by adding AI Question Generator nodes if there is a relevant capability.
 *
 * @param global_navigation $navigation An object representing the navigation tree.
 */
function local_ai_question_gen_extend_navigation(global_navigation $navigation) {
    global $PAGE;
    
    if (has_capability('local/ai_question_gen:generate', context_system::instance())) {
        $node = $navigation->add(
            get_string('pluginname', 'local_ai_question_gen'),
            new moodle_url('/local/ai_question_gen/index.php'),
            navigation_node::TYPE_CUSTOM,
            null,
            'ai_question_gen',
            new pix_icon('i/questions', '')
        );
        $node->showinflatnavigation = true;
    }
}

/**
 * Add nodes to myprofile page.
 *
 * @param \core_user\output\myprofile\tree $tree Tree object
 * @param stdClass $user user object
 * @param bool $iscurrentuser
 * @param stdClass $course Course object
 */
function local_ai_question_gen_myprofile_navigation(core_user\output\myprofile\tree $tree, $user, $iscurrentuser, $course) {
    if (has_capability('local/ai_question_gen:generate', context_system::instance())) {
        $url = new moodle_url('/local/ai_question_gen/index.php');
        $node = new core_user\output\myprofile\node('miscellaneous', 'ai_question_gen',
                get_string('pluginname', 'local_ai_question_gen'), null, $url);
        $tree->add_node($node);
    }
}

/**
 * Serves the plugin files.
 *
 * @param stdClass $course course object
 * @param stdClass $cm course module object
 * @param stdClass $context context object
 * @param string $filearea file area
 * @param array $args extra arguments
 * @param bool $forcedownload whether or not force download
 * @param array $options additional options affecting the file serving
 * @return bool false if file not found, does not return if found - just send the file
 */
function local_ai_question_gen_pluginfile($course, $cm, $context, $filearea, $args, $forcedownload, array $options = array()) {
    // Check the contextlevel is as expected - if your plugin is a block, this becomes CONTEXT_BLOCK, etc.
    if ($context->contextlevel != CONTEXT_SYSTEM) {
        return false;
    }

    // Make sure the filearea is one of those used by the plugin.
    if ($filearea !== 'content') {
        return false;
    }

    // Make sure the user is logged in and has access to the module.
    require_login();

    // Check the relevant capabilities - these may vary depending on the filearea being accessed.
    if (!has_capability('local/ai_question_gen:generate', $context)) {
        return false;
    }

    // Leave this line out if you set the itemid to null in make_pluginfile_url (set $itemid to 0 instead).
    $itemid = array_shift($args); // The first item in the $args array.

    // Use the itemid to retrieve any relevant data records and perform any security checks to see if the
    // user really does have access to the file in question.

    // Extract the filename / filepath from the $args array.
    $filename = array_pop($args); // The last item in the $args array.
    if (!$args) {
        $filepath = '/'; // $args is empty => the path is '/'
    } else {
        $filepath = '/'.implode('/', $args).'/'; // $args contains elements of the filepath
    }

    // Retrieve the file from the Files API.
    $fs = get_file_storage();
    $file = $fs->get_file($context->id, 'local_ai_question_gen', $filearea, $itemid, $filepath, $filename);
    if (!$file) {
        return false; // The file does not exist.
    }

    // We can now send the file back to the browser - in this case with a cache lifetime of 1 day and no filtering.
    send_stored_file($file, 86400, 0, $forcedownload, $options);
}
