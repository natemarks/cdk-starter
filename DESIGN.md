# Design


## Infrastructure As Code


The entrypoint for CDK is always app.py. It uses the stack modules to deploy
stacks.  If you have multiple environments, you might use app.py to decide
whch stacks to deploy ine ach environment and use environment-specific
configration data to deploy the stacks.  This can make app.py pretty lengthy,
so I create an inventory,.py module. It figures out which stacks should be
deployed in each environemt and provides the correct configuration data.

NOTE: configuration data MUST NOT be sensitive data, like keys and credentials.
I keep those in secretsmanager or similar. I use configuration data for things
like environment-specific naming/scaling, etc.

### Example Stacks





## Project Automation: GNU make


## AWS CDK Stack Operations: ls/deploy/destroy/synth
The core logic of this project uses CDK to manage cloudformation  stacks

The project also contias configuration data.
 - configuration data must not be sensitive (credentials, keys, etc.). Sensitive data should be in secretsmanager or similar
 - configuration data may be  edited manually OR updated with discovery automation
 - configuration data is stored in a per-environment  directory containing JSON files



configuration data is organized into JSON files that are place in a fixed location relative to an enviornment directory.  This makes it easy to use dataclasses to manage the data in the JSON files. These dataclasses are called 'settings'. 

example configuratiojn data storage  for the dev environment


dev/
dev/environment.json -> contains environment-wide configuration data
dev/stack1.json  -> a setting file containing some data required by stack1
dev/stack2/alpha1.json -> a setting files containing some data requried by stack2

This structure is used to make it easy to manage real and test data.




Every stack is created by a Stack class. Each stack class has a unique stack input class. The stack input classes are composed of one or more settings objects

## External Data Discovery
