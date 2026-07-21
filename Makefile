.PHONY: lint test backend-lint backend-test frontend-lint frontend-test

lint: frontend-lint backend-lint

test: frontend-test backend-test

frontend-lint:
	npm run lint
	npx tsc --noEmit

frontend-test:
	npm test -- --ci

backend-lint:
	cd backend && ruff check app tests
	cd backend && mypy --strict app

backend-test:
	cd backend && pytest tests/ --cov=app --cov-fail-under=80
