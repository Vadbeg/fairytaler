.PHONY: format lint type-check clean

# Variables
PYTHON = python
CODE_DIRS = .

# Format code with black
format:
	black $(CODE_DIRS)
	ruff check --fix $(CODE_DIRS)
	isort $(CODE_DIRS)



# Run type checking
type-check:
	mypy $(CODE_DIRS)

# Run all code quality checks
check: format lint type-check

# Clean up python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
