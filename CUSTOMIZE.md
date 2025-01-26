# customize



## Changing names but keep the tests working
If you want to create a new project from this one, I'd start by just renaming
the high level project constants, while making sure the project test continue
to pass.

** new project name**

you'll want to change 'cdk-starter' (ex. 'cdk-oranges')

Create the new project directory and clone cdk-starter into it:

```console
foo@bar:~$ mkdir -p ~/projects/cdk-oranges
foo@bar:~$ git clone git@github.com:natemarks/cdk-starter.git ~/projects/cdk-oranges/
Cloning into '/home/nmarks/projects/cdk-oranges'...
remote: Enumerating objects: 144, done.
remote: Counting objects: 100% (144/144), done.
remote: Compressing objects: 100% (77/77), done.
remote: Total 144 (delta 37), reused 132 (delta 27), pack-reused 0 (from 0)
Receiving objects: 100% (144/144), 41.80 KiB | 1.49 MiB/s, done.
Resolving deltas: 100% (37/37), done.
# create a new  git repo
foo@bar:~$ cd ~/project/cdk-oranges
foo@bar:~$ rm -rf .git
foo@bar:~$ git init . && git add --all && git commit -v -a


```

Customize the project with the following changes

You may want a new repo. I use 'github.com/natemarks/cdk-starter' in the
resource tags:

```
# app.py
cdk.Tags.of(app).add("iac", "github.com/natemarks/cdk-starter")
```

** app name **

You'll want a new App name. I use 'Starter' at the beginning of every resource
name for this project. It's configured here:
```
# config/helper.py
APP_NAME = "Starter"
```


** AWS Account **

I use the AWS account number to raise an exception if I try to deploy a stack
in the wrong aws account. I've absolutely made that mistake before :D

```
# config/helper.py
APP_ENV_TO_AWS_ACCOUNT = {
    "dev": "709310380790",
    "staging": "709310380790",
    "production": "709310380790",
}
```


** AWS Region **
The AWS region is specified in the 'default_region' attribte of the
EnvironmentSetting for each environment. That means it's stored in these JSON
files:

- dev: config/dev/environment.json
- staging: config/staging/environment.json
- production: config/production/environment.json




Run 'make static'. The tests should fail because the template resource names
won't match the expected ones. Run 'make unit-update_golden'. That should pass.
