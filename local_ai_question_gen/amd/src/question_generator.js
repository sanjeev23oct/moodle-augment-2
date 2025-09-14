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
 * JavaScript module for AI Question Generator.
 *
 * @module     local_ai_question_gen/question_generator
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

define(['jquery', 'core/ajax', 'core/notification', 'core/modal_factory', 'core/modal_events'], 
function($, Ajax, Notification, ModalFactory, ModalEvents) {
    
    'use strict';
    
    /**
     * Initialize the question generator interface.
     */
    function init() {
        bindEvents();
        initializeSortable();
    }
    
    /**
     * Bind event handlers.
     */
    function bindEvents() {
        // Form submission for question generation
        $('#question-generation-form').on('submit', handleQuestionGeneration);
        
        // Regenerate questions
        $('#regenerate-btn').on('click', handleRegenerate);
        
        // Add manual question
        $('#add-manual-btn').on('click', handleAddManual);
        
        // Edit question buttons
        $(document).on('click', '.edit-question-btn', handleEditQuestion);
        
        // Delete question buttons
        $(document).on('click', '.delete-question-btn', handleDeleteQuestion);
        
        // Export functionality
        $('#export-btn').on('click', handleExport);
        
        // Auto-save session name
        $('#session-name').on('blur', handleSessionNameChange);
    }
    
    /**
     * Handle question generation form submission.
     */
    function handleQuestionGeneration(e) {
        e.preventDefault();
        
        var formData = {
            sesskey: $('input[name="sesskey"]').val(),
            session_id: $('input[name="session_id"]').val() || 0,
            session_name: $('#session-name').val().trim(),
            content: $('#content-text').val().trim(),
            question_type: $('input[name="question_type"]:checked').val(),
            question_count: $('#question-count').val()
        };
        
        // Validate form
        if (!formData.session_name) {
            Notification.alert('Error', 'Please enter a session name');
            return;
        }
        
        if (!formData.content) {
            Notification.alert('Error', 'Please enter some content');
            return;
        }
        
        if (formData.content.length < 50) {
            Notification.alert('Error', 'Content is too short. Please provide at least 50 characters.');
            return;
        }
        
        showLoading(true);
        
        // Call the generation service
        Ajax.call([{
            methodname: 'local_ai_question_gen_generate_questions',
            args: formData
        }])[0].done(function(response) {
            showLoading(false);
            if (response.success) {
                handleGenerationSuccess(response);
            } else {
                Notification.alert('Error', response.message || 'Failed to generate questions');
            }
        }).fail(function(error) {
            showLoading(false);
            Notification.alert('Error', 'Failed to generate questions: ' + error.message);
        });
    }
    
    /**
     * Handle successful question generation.
     */
    function handleGenerationSuccess(response) {
        // Show success message
        Notification.addNotification({
            message: 'Questions generated successfully!',
            type: 'success'
        });
        
        // Redirect to the session page to show generated questions
        if (response.session_id) {
            window.location.href = '?session_id=' + response.session_id;
        } else {
            // Reload page to show updated content
            window.location.reload();
        }
    }
    
    /**
     * Handle regenerate questions.
     */
    function handleRegenerate(e) {
        e.preventDefault();
        
        // Show confirmation dialog
        Notification.confirm(
            'Confirm Regeneration',
            'Are you sure you want to regenerate questions? This will replace existing questions.',
            'Regenerate',
            'Cancel',
            function() {
                // Trigger form submission
                $('#question-generation-form').trigger('submit');
            }
        );
    }
    
    /**
     * Handle add manual question.
     */
    function handleAddManual(e) {
        e.preventDefault();
        
        // Create modal for manual question creation
        ModalFactory.create({
            type: ModalFactory.types.SAVE_CANCEL,
            title: 'Add Manual Question',
            body: getManualQuestionForm()
        }).done(function(modal) {
            modal.getRoot().on(ModalEvents.save, function() {
                handleSaveManualQuestion(modal);
            });
            modal.show();
        });
    }
    
    /**
     * Get manual question form HTML.
     */
    function getManualQuestionForm() {
        return '<form id="manual-question-form">' +
            '<div class="form-group">' +
                '<label for="manual-question-text">Question Text</label>' +
                '<textarea id="manual-question-text" class="form-control" rows="3" required></textarea>' +
            '</div>' +
            '<div class="form-group">' +
                '<label for="manual-question-type">Question Type</label>' +
                '<select id="manual-question-type" class="form-control" required>' +
                    '<option value="mcq">Multiple Choice</option>' +
                    '<option value="short_answer">Short Answer</option>' +
                    '<option value="fill_blanks">Fill in the Blanks</option>' +
                    '<option value="truefalse">True/False</option>' +
                '</select>' +
            '</div>' +
            '<div id="manual-question-options"></div>' +
        '</form>';
    }
    
    /**
     * Handle edit question.
     */
    function handleEditQuestion(e) {
        e.preventDefault();
        var questionId = $(e.currentTarget).data('question-id');
        
        // Load question data and show edit modal
        Ajax.call([{
            methodname: 'local_ai_question_gen_get_question',
            args: {question_id: questionId}
        }])[0].done(function(question) {
            showEditQuestionModal(question);
        }).fail(function(error) {
            Notification.alert('Error', 'Failed to load question: ' + error.message);
        });
    }
    
    /**
     * Show edit question modal.
     */
    function showEditQuestionModal(question) {
        var modal = $('#question-edit-modal');
        
        // Populate modal with question data
        modal.find('.modal-body').html(getEditQuestionForm(question));
        modal.modal('show');
        
        // Handle save button
        $('#save-question-btn').off('click').on('click', function() {
            handleSaveQuestion(question.id, modal);
        });
    }
    
    /**
     * Get edit question form HTML.
     */
    function getEditQuestionForm(question) {
        // This would be expanded based on question type
        return '<form id="edit-question-form">' +
            '<div class="form-group">' +
                '<label for="edit-question-text">Question Text</label>' +
                '<textarea id="edit-question-text" class="form-control" rows="3">' + question.question_text + '</textarea>' +
            '</div>' +
            '<div class="form-group">' +
                '<label for="edit-difficulty">Difficulty</label>' +
                '<select id="edit-difficulty" class="form-control">' +
                    '<option value="easy"' + (question.difficulty === 'easy' ? ' selected' : '') + '>Easy</option>' +
                    '<option value="medium"' + (question.difficulty === 'medium' ? ' selected' : '') + '>Medium</option>' +
                    '<option value="hard"' + (question.difficulty === 'hard' ? ' selected' : '') + '>Hard</option>' +
                '</select>' +
            '</div>' +
            // Add more fields based on question type
        '</form>';
    }
    
    /**
     * Handle delete question.
     */
    function handleDeleteQuestion(e) {
        e.preventDefault();
        var questionId = $(e.currentTarget).data('question-id');
        
        // Show confirmation dialog
        Notification.confirm(
            'Confirm Deletion',
            'Are you sure you want to delete this question?',
            'Delete',
            'Cancel',
            function() {
                deleteQuestion(questionId);
            }
        );
    }
    
    /**
     * Delete a question.
     */
    function deleteQuestion(questionId) {
        Ajax.call([{
            methodname: 'local_ai_question_gen_delete_question',
            args: {question_id: questionId}
        }])[0].done(function(response) {
            if (response.success) {
                // Remove question from DOM
                $('[data-question-id="' + questionId + '"]').fadeOut(function() {
                    $(this).remove();
                });
                
                Notification.addNotification({
                    message: 'Question deleted successfully!',
                    type: 'success'
                });
            } else {
                Notification.alert('Error', response.message || 'Failed to delete question');
            }
        }).fail(function(error) {
            Notification.alert('Error', 'Failed to delete question: ' + error.message);
        });
    }
    
    /**
     * Handle export functionality.
     */
    function handleExport(e) {
        e.preventDefault();
        
        // For now, just show a placeholder message
        Notification.alert('Export', 'Export functionality will be implemented in the next phase.');
    }
    
    /**
     * Handle session name change.
     */
    function handleSessionNameChange(e) {
        var sessionId = $('input[name="session_id"]').val();
        var sessionName = $(e.target).val().trim();
        
        if (sessionId && sessionName) {
            // Auto-save session name
            Ajax.call([{
                methodname: 'local_ai_question_gen_update_session',
                args: {
                    session_id: sessionId,
                    session_name: sessionName
                }
            }])[0].done(function(response) {
                if (response.success) {
                    // Show subtle success indicator
                    $(e.target).addClass('is-valid').removeClass('is-invalid');
                    setTimeout(function() {
                        $(e.target).removeClass('is-valid');
                    }, 2000);
                }
            }).fail(function() {
                $(e.target).addClass('is-invalid').removeClass('is-valid');
            });
        }
    }
    
    /**
     * Initialize sortable functionality for questions.
     */
    function initializeSortable() {
        // This would implement drag-and-drop reordering
        // For now, just a placeholder
        console.log('Sortable functionality will be implemented');
    }
    
    /**
     * Show/hide loading indicator.
     */
    function showLoading(show) {
        if (show) {
            $('#generate-btn, #regenerate-btn').prop('disabled', true);
            $('#loading-indicator').removeClass('d-none');
        } else {
            $('#generate-btn, #regenerate-btn').prop('disabled', false);
            $('#loading-indicator').addClass('d-none');
        }
    }
    
    return {
        init: init
    };
});
