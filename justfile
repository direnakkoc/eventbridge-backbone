bootstrap:
	pip install --upgrade pip pre-commit poetry==1.7.1
	pre-commit install
	poetry config --local virtualenvs.in-project true
	poetry install
	npm install -g aws-cdk@^2

package:
	@echo "Packaging common deps Lambda layer"
	rm -rf .build
	mkdir -p .build/common_layer ; poetry export --without=dev --without-hashes --format=requirements.txt > .build/common_layer/requirements.txt

	@echo "Packaging Lambda functions"
	mkdir -p .build/handlers/
	rm -rf dist
	poetry build --format wheel
	unzip dist/*.whl -x 'cdk/*' '*.dist-info/*' -d .build/handlers/

lint: pre-commit

lint-fix:
	@echo "Running black"
	poetry run black .
	@echo "Running ruff"
	poetry run ruff check --fix .

lint-strict: lint
	@echo "Running mypy"
	poetry run mypy --pretty handlers cdk tests

pre-commit:
	pre-commit run --all-files

test-unit:
	poetry run pytest tests/unit --cov-config=.coveragerc --cov=handlers --cov-report=term

test-int:
	poetry run pytest tests/integration

test-infra: package
	poetry run pytest tests/infrastructure

test-e2e:
	poetry run pytest tests/e2e

dev-synth:
	./scripts/dev-user-stack.sh synth

dev-deploy:
	./scripts/dev-user-stack.sh deploy --no-cdk-approval

dev-destroy:
	./scripts/dev-user-stack.sh destroy
