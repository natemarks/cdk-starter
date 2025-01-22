# Design

The purpose oif this project is not to deploy and manage infrastructure as code. The purpose is to demonstrate some useful techniques for an AWS CDK (Python) project. 


## Project Automation
dfljkgb

### Automate Static checks with GNU make

 - black /swapfile
 - pylint
 - shellcheck

### Test Automation

 - execute unit tests
 - update unit test golden files
 - execute aws tests
 - update aws unit test golden files

### Update CDK Library
 - update cdk libraries

### CDK Commands

 - automate cdk commands

### Update Configuration Data from External Sources

The project also contias configuration data.
 - configuration data must not be sensitive (credentials, keys, etc.). Sensitive data should be in secretsmanager or similar
 - configuration data may be  edited manually OR updated with discovery automation
 - configuration data is stored in a per-environment  directory containing JSON files

 - update config files with external data

## Example Infrastructure

### AppVpc

stack /settings/input

### SimpleAsg

stack /settings /input


