# CLAUDE.md - Coding Guidelines

## Commands
- Run tests: `pytest path/to/test.py`
- Lint Python: `flake8 path/to/file.py`
- Install dependencies: `pip install -r requirements.txt`
- Create virtual environment: `python -m venv .venv && source .venv/bin/activate`
- Run Python script: `python /home/koom/hackery2/src/hackery2/bin/script.py`
- Track development intentions: `intention add "Working on feature X"`, `intention show`, `intention clear`
- **IMPORTANT**: Always set intentions before starting new features or bug fixes using `intention add`

## Code Style
- Dont Repeat Yourself!
- Indentation: Tabs for Python, 4 spaces for bash scripts
- Naming: snake_case for functions/variables, CamelCase for classes
- Imports: Group standard library first, then third-party, then local modules
- Variables: Use descriptive names; avoid single-letter except for counters
- Line length: Keep under 100 characters when possible

## File Organization
- Python scripts: Place in `/src/hackery2/lib/` (preferred) or `/src/hackery2/bin/`
- Fish functions: Place in `/setup/data/fish/functions/`
- Configuration files: Place in `/setup/data/`
- Project modules: Create descriptive folders in `/data/`

## Python Best Practices
- Error handling: Use specific exceptions with informative messages
- Shell commands: Use `subprocess` module with proper error handling
- Parameters: Use argument parser for scripts with multiple options, prefer python click