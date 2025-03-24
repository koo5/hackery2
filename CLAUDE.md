# CLAUDE.md - Coding Guidelines

## Commands
- Run tests: No standardized test command found
- Lint: No standardized lint command found
- Run single test: pytest path/to/test.py
- Install dependencies: pip install -r requirements.txt

## Code Style
- Indentation: Tabs for Python, 4 spaces for bash scripts
- Naming: snake_case for functions and variables
- File structure: Related code in modules under src/hackery2/bin/
- Functions: Short, focused functions with descriptive names
- Error handling: Use try/except with specific exceptions
- Imports: Group standard library imports first, then third-party

## Fish Functions
- Simple one-line commands in dedicated .fish files
- Place in setup/data/fish/functions/
- Follow existing patterns (see gr.fish, gs.fish)

## Python Best Practices
- Document with docstrings for classes
- Use relative imports for project modules
- Keep files focused on single responsibility
- Handle errors explicitly with informative messages