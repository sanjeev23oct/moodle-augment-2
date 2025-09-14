# AI Question Generator Plugin for Moodle

An AI-powered Moodle plugin that automatically generates questions from chapter content using artificial intelligence.

## Features

- **AI-Powered Generation**: Generate questions automatically from text content
- **Multiple Question Types**: Support for MCQ, Short Answer, Fill-in-the-Blanks, and True/False questions
- **Session Management**: Organize questions into named sessions for easy management
- **Question Editing**: Edit generated questions or create manual questions
- **Responsive Interface**: Modern, mobile-friendly user interface
- **Export Functionality**: Export questions to various formats (future feature)

## Requirements

- Moodle 4.3 or higher
- PHP 8.0 or higher
- PostgreSQL or MySQL database
- AI API access (OpenAI or Anthropic) - for production use

## Installation

### Method 1: Manual Installation

1. Download or clone this repository
2. Copy the `local_ai_question_gen` folder to your Moodle's `local/` directory
3. Navigate to `Site Administration > Notifications` in your Moodle admin panel
4. Follow the installation prompts to install the plugin

### Method 2: Direct Copy to Moodle

```bash
# Copy plugin to Moodle local directory
cp -r local_ai_question_gen /path/to/your/moodle/local/

# Set proper permissions
chmod -R 755 /path/to/your/moodle/local/local_ai_question_gen
```

For Windows (XAMPP):
```cmd
# Copy to XAMPP Moodle directory
xcopy local_ai_question_gen D:\xampp\moodle\local\ai_question_gen /E /I

# Or use the file explorer to copy the folder
```

## Configuration

1. Go to `Site Administration > Plugins > Local plugins > AI Question Generator`
2. Configure the following settings:
   - **OpenAI API Key**: Your OpenAI API key (optional for testing)
   - **Anthropic API Key**: Your Anthropic API key (optional for testing)
   - **Default AI Provider**: Choose between OpenAI or Anthropic
   - **Maximum Questions per Request**: Limit questions generated per request (default: 10)
   - **Cache Duration**: How long to cache AI responses in hours (default: 24)

## Usage

### For Teachers and Content Creators

1. Navigate to the AI Question Generator from the main navigation menu
2. Enter a session name for your question set
3. Paste your chapter content into the text area
4. Select the type of questions you want to generate
5. Choose the number of questions (1-10)
6. Click "Generate" to create questions automatically

### Managing Questions

- **Edit Questions**: Click the edit button on any question to modify it
- **Delete Questions**: Remove unwanted questions with the delete button
- **Add Manual Questions**: Create questions manually using the "Add Manual Question" button
- **Reorder Questions**: Drag and drop questions to reorder them (future feature)

### Session Management

- **Save Sessions**: Questions are automatically saved in named sessions
- **Load Sessions**: Access previous sessions from the dropdown menu
- **Duplicate Sessions**: Create copies of existing sessions (future feature)

## Current Status

This plugin is currently in **Alpha** stage with the following features implemented:

✅ **Completed Features:**
- Basic plugin structure and database schema
- User interface for question generation
- Session and question management
- Mock question generation (for testing UI)
- Responsive design
- Basic AJAX functionality

🚧 **In Development:**
- AI service integration (Python service)
- Question export functionality
- Advanced question editing
- Drag-and-drop reordering

📋 **Planned Features:**
- PDF/DOCX file upload support
- Question bank integration
- Advanced analytics and reporting
- Multi-language support
- Collaborative question creation

## Testing

The plugin currently uses mock data for question generation to allow testing of the user interface without requiring AI API access. This makes it perfect for:

- UI/UX testing
- Database functionality testing
- Session management testing
- Basic workflow validation

## Development

### File Structure

```
local_ai_question_gen/
├── db/                     # Database definitions
│   ├── install.xml         # Database schema
│   ├── access.php          # Capabilities
│   └── upgrade.php         # Upgrade scripts
├── lang/en/                # Language files
│   └── local_ai_question_gen.php
├── classes/                # PHP classes
│   ├── ai/                 # AI provider interfaces
│   ├── manager/            # Data managers
│   └── service/            # Business logic services
├── templates/              # Mustache templates
├── amd/src/               # JavaScript modules
├── ajax/                  # AJAX endpoints
├── version.php            # Plugin metadata
├── lib.php               # Plugin functions
├── settings.php          # Admin settings
├── index.php             # Main interface
└── styles.css            # Custom styles
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Plugin not appearing in navigation**
   - Check user capabilities: `local/ai_question_gen:generate`
   - Verify plugin installation completed successfully

2. **Database errors during installation**
   - Ensure your Moodle database user has CREATE TABLE permissions
   - Check Moodle logs for specific error messages

3. **JavaScript not working**
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Verify AMD module loading

### Debug Mode

Enable debug mode in the plugin settings to get additional logging information.

## License

This plugin is licensed under the GNU General Public License v3.0. See the LICENSE file for details.

## Support

For support and questions:
- Check the Moodle forums
- Review the plugin documentation
- Submit issues on the project repository

## Changelog

### Version 1.0.0 (Alpha)
- Initial plugin structure
- Basic UI implementation
- Mock question generation
- Session management
- Database schema
- Admin settings interface

---

**Note**: This plugin is currently in development. The AI integration will be completed in the next phase through a separate Python service.
