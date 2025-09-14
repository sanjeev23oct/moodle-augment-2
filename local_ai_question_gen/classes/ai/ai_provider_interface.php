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
 * AI Provider Interface for AI Question Generator plugin.
 *
 * @package    local_ai_question_gen
 * @copyright  2024 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_ai_question_gen\ai;

/**
 * Interface for AI providers that can generate questions.
 */
interface ai_provider_interface {
    
    /**
     * Generate questions from content using AI.
     *
     * @param string $content The content to generate questions from
     * @param string $type The type of questions to generate (mcq, short_answer, fill_blanks)
     * @param int $count Number of questions to generate
     * @param array $options Additional options for generation
     * @return array Array of generated questions
     * @throws \moodle_exception If generation fails
     */
    public function generate_questions(string $content, string $type, int $count, array $options = []): array;
    
    /**
     * Validate the API configuration.
     *
     * @return bool True if API is properly configured
     */
    public function validate_api_key(): bool;
    
    /**
     * Get the provider name.
     *
     * @return string Provider name
     */
    public function get_provider_name(): string;
    
    /**
     * Get rate limits for this provider.
     *
     * @return array Rate limit information
     */
    public function get_rate_limits(): array;
    
    /**
     * Format prompt for the AI provider.
     *
     * @param string $content The content to generate questions from
     * @param string $type The type of questions to generate
     * @param int $count Number of questions to generate
     * @param array $options Additional options
     * @return string Formatted prompt
     */
    public function format_prompt(string $content, string $type, int $count, array $options = []): string;
    
    /**
     * Parse and validate AI response.
     *
     * @param array $response Raw response from AI API
     * @param string $type Expected question type
     * @return array Parsed and validated questions
     * @throws \moodle_exception If response is invalid
     */
    public function parse_response(array $response, string $type): array;
    
    /**
     * Get supported question types for this provider.
     *
     * @return array Array of supported question types
     */
    public function get_supported_types(): array;
    
    /**
     * Get maximum content length supported by this provider.
     *
     * @return int Maximum content length in characters
     */
    public function get_max_content_length(): int;
    
    /**
     * Get maximum number of questions that can be generated in one request.
     *
     * @return int Maximum question count
     */
    public function get_max_question_count(): int;
    
    /**
     * Check if the provider is available and configured.
     *
     * @return bool True if provider is available
     */
    public function is_available(): bool;
    
    /**
     * Get estimated cost for generating questions.
     *
     * @param string $content Content to analyze
     * @param int $count Number of questions
     * @return float Estimated cost in USD
     */
    public function estimate_cost(string $content, int $count): float;
}
