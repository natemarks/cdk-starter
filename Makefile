.DEFAULT_GOAL := help

# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
SHELL := $(shell which bash)
DEFAULT_BRANCH := main
VERSION := 0.0.0
COMMIT := $(shell git rev-parse HEAD)
CDK := node_modules/.bin/cdk

CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
DEFAULT_BRANCH := main
app_env := sandbox
PYTHON_VERSION := 3.10.6
CDK_VERSION := 2.70.0

help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

clean-venv: ## re-create virtual env
	[[ -e .venv ]] && rm -rf .venv; \
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python3 -m venv .venv; \
       source .venv/bin/activate; \
       pip install --upgrade pip setuptools; \
       pip install -r requirements.txt; \
    )

.venv: ## create venv if it doesnt exist
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python3 -m venv .venv; \
       source .venv/bin/activate; \
       pip install --upgrade pip setuptools; \
       pip install -r requirements.txt; \
    )

update_cdk_libs: ## install the latest version of aws cdk node and python packages
	bash scripts/update_cdk_libs.sh
	$(MAKE) clean-venv

pylint: ## run pylint on python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' | xargs pylint --max-line-length=90; \
    )

black: ## use black to format python files
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' |  xargs black --line-length=79; \
    )

black-check: ##  fail if there are formatting propblems
	( \
       . .venv/bin/activate; \
       git ls-files '*.py' |  xargs black --check --line-length=79; \
    )

shellcheck: ## use black to format python files
	( \
       git ls-files 'scripts/*.sh' |  xargs shellcheck --format=gcc; \
    )

unit-test: ## run test that have no external dependencies
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "unit" tests/; \
    )

unit-update_golden: ## update update golden files with latest results
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "unit" tests/ --update_golden; \
    )

aws-test: ## run test that require aws credentials
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "aws" tests/; \
    )

aws-update_golden: ## update golden files with actual results
	( \
       source .venv/bin/activate; \
       python3 -m pytest -v -m "aws" tests/ --update_golden; \
    )

static: shellcheck black pylint unit-test ##  run all static checks

clean-cache: ## clean python adn pytest cache data
	@find . -type f -name "*.py[co]" -delete -not -path "./.venv/*"
	@find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} \;
	@rm -rf .pytest_cache

git-status: ## require status is clean so we can use undo_edits to put things back
	@status=$$(git status --porcelain); \
	if [ ! -z "$${status}" ]; \
	then \
		echo "Error - working directory is dirty. Commit those changes!"; \
		exit 1; \
	fi

undo_edits: ##  reset changes to HEAD
	git reset HEAD --hard
	git clean -f

node_modules: ## create node_modules/ if it doesn't exist
	bash scripts/update_cdk_libs.sh $(CDK_VERSION)
	$(MAKE) clean-venv

cdk-ls: node_modules  ## run cdk ls
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) ls -c app_env=$(app_env); \
    )

cdk-diff: node_modules  ## cdk diff a single stack
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) diff $(stack) -c app_env=$(app_env); \
    )

cdk-diff-all: node_modules  ## cdk diff all stacks in the envirnment
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) diff --all -c app_env=$(app_env); \
    )

cdk-deploy: node_modules  ## cdk deploy a single stack
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	# source the pyenv config script
	# set the local python version. redundant but harmless
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) deploy --require-approval never $(stack) -c app_env=$(app_env); \
    )

cdk-destroy: node_modules  ## cdk destroy a single stack
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	# source the pyenv config script
	# set the local python version. redundant but harmless
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) destroy --force $(stack) -c app_env=$(app_env); \
    )

cdk-deploy-all: node_modules  ## cdk deploy all stacks in an environment
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	# source the pyenv config script
	# set the local python version. redundant but harmless
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) deploy --all $(stack) -c app_env=$(app_env); \
    )

cdk-bootstrap: node_modules  ## bootstrap the default account and region for an environment
	# cdk executable usually: node_modules/aws-cdk/bin/cdk
	# have to be evaluated after the node_modules target
	$(eval CDK := $(shell find . -type f -name cdk))
	# source the pyenv config script
	# set the local python version. redundant but harmless
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       $(CDK) $(shell bash scripts/cdk_bootstrap.sh) -c app_env=$(app_env); \
    )


discover: ## update environment config data with discovered information
	( \
       source scripts/enable_pyenv.sh; \
       pyenv local $(PYTHON_VERSION); \
       python --version; \
       source .venv/bin/activate; \
       PYTHONPATH="." python3 discover.py $(app_env); \
    )

.PHONY: build static test artifact	
