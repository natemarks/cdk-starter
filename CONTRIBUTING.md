# Contributing
help:  Show this help.
clean-venv:  re-create virtual env
.venv:  create venv if it doesnt exist
update_cdk_libs:  install the latest version of aws cdk node and python packages
pylint:  run pylint on python files
black:  use black to format python files
black-check:  use black to format python files
shellcheck:  use black to format python files
unit-test:  run test that have no external dependencies
unit-update_golden:  update update golden files with latest results
aws-test:  run test that require aws credentials
aws-update_golden:  update golden files with actual results
static: shellcheck black pylint unit-test  run all static checks
clean-cache:  clean python adn pytest cache data
git-status:  require status is clean so we can use undo_edits to put things back
undo_edits:  the build process has to edit files. run this to put things back
rebase: git-status  rebase current feature branch on to the default branch
node_modules:  create node_modules/ if it doesn't exist
cdk-ls: node_modules   run cdk ls
cdk-diff: node_modules   run cdk diff
cdk-diff-all: node_modules   run cdk diff
cdk-synth: node_modules   run cdk synth
cdk-deploy: node_modules   run cdk deploy
cdk-destroy: node_modules   run cdk deploy
cdk-deploy-all: node_modules   run cdk deploy
cdk-bootstrap: node_modules   run cdk deploy
discover:  discover configuration data

## branch protection


## pipeline support


## debugger support

## resource tagging

## reproducible pipeline automation 
make deploy locally works exactly the same way in a pipeline



stack  creation
input and settings
dev setting files
stack
static checks
stack unit test
cdk-ls



