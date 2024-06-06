lints: ## to trigger ruff lint, black formatter and isort util
	black .
	isort .
	ruff check .
