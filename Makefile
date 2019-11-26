SHELL = /usr/bin/env bash -xeuo pipefail
stack_name=bookmarks-api

isort:
	pipenv run isort -rc \
		src/ \
		tests/

lint:
	pipenv run flake8 \
		src/ \
		tests/

format:
	pipenv run black \
		src/ \
		tests/

package:
	rm -rf dist
	mkdir dist
	pipenv run aws cloudformation package \
		--template-file sam.yml \
		--s3-bucket $$ARTIFACTS_S3_BUCKET \
		--output-template-file dist/template.yml

deploy: package
	pipenv run aws cloudformation deploy \
		--template-file dist/template.yml \
		--stack-name $(stack_name) \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset
	pipenv run aws cloudformation describe-stacks \
		--stack-name $(stack_name) \
		--query 'Stacks[0].Outputs'

test-unit:
	@for test_dir in $$(find tests/unit -maxdepth 1 -type d); do \
		handler=$$(basename $$test_dir); \
		if [[ $$handler =~ unit|__pycache__ ]]; then continue; fi; \
		PYTHONPATH=src/layer/python \
		pipenv run pytest $$test_dir --cov-config=setup.cfg --cov=src/layer/python/$$handler; \
	done
