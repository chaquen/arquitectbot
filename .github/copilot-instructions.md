# GitHub Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a Flask-based API project for managing architectural components. When suggesting code:

1. Follow RESTful API best practices
2. Use SQLAlchemy for database operations
3. Implement proper error handling and validation
4. Write code that is testable with pytest
5. Follow the existing project structure:
   - Models in `app/models.py`
   - Routes in `app/routes.py`
   - Business logic in `app/services.py`
   - Request handling in `app/controllers.py`
6. Include appropriate type hints and docstrings
7. Follow PEP 8 style guidelines
