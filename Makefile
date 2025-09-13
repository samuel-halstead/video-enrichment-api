# Bump these on release
VERSION_MAJOR ?= 0
VERSION_MINOR ?= 1
VERSION_PATCH ?= 0
CHART_PATH ?= chart/

VERSION ?= $(VERSION_MAJOR).$(VERSION_MINOR).$(VERSION_PATCH)

K8_NS ?= default
PROJECT ?= video-enrichment-api

.PHONY: install
install:
	poetry lock -n
	poetry install -n
	poetry run pre-commit install

# Do quality checks
.PHONY: quality
quality:
	poetry run black .
	poetry run isort . --profile black
	poetry run ruff --fix .

# Do testing
.PHONY: tests
tests:
	poetry run python -m pytest

# Retrieve the version variable
.PHONY: version
version:
	@echo $(VERSION)

# Update required files with provided version number
.PHONY: bumpversion
bumpversion:
	poetry version $(VERSION)
	python bumpversion.py $(VERSION)

# Deploy the package with Helm to the Kubernetes namespace
# TODO: parametrizable namespace.
.PHONY: deploy
deploy:
	helm install -n $(K8_NS) python-project -f ./deploy/helm-values.yaml chart/

.PHONY: delete-deploy
delete-deploy:
	helm uninstall -n $(K8_NS) $(PROJECT)

.PHONY: configure-kubernetes
configure-kubernetes:
	aws eks update-kubeconfig --name delivery-platform --region eu-west-1

.PHONY: port-forward
port-forward:
	kubectl port-forward -n $(K8_NS) service/$(PROJECT) 8080:8080

.PHONY: name
name:
	@cat ${CHART_PATH}/Chart.yaml | grep name | cut -d " " -f 2