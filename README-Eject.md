# NX1 / Citadel

This repository contains infrastructure originally created by NX1/Citadel.

## Tools

Sceptre is used to maintain cloudformation stacks.

Using Sceptre, we can store the meta information about a stack in a YAML file, and Sceptre is able to compare and update differences in a deterministic way.

Learn more about Sceptre at https://docs.sceptre-project.org/.

## Initial Configuration

### Introduction

A script called `eject.py` can be found in this repository.

This script will connect to an AWS account and scan a passed region for cloudformation stacks that their names starts with `citadel-*` or `StackSet-citadel-*`. These were stacks created by NX1/Citadel.

Once scanned, the script will download the cloudformation templates to the `templates/<account_name>/<region>/<stack_name>.yaml`

And fetch the meta information about a stack (parameters, iam role, etc) and write to another YAML file in a format understood by Sceptre. This file is located at `config/<account_name>/<region>/<stack_name>.yaml`.

The scripts **makes no changes** to your AWS account, it can be ran with read-only permissions.

### Running

You need first to set credentials to access the AWS account that you wish to eject from NX1/Citadel. These credentials can be read-only.

Then, from the root of this repository, run:
```
python3 eject.py --account-name dev --region ap-southeast-2
```

Change the `account-name` and `region` for the desired ones.

Once the script finish running, a file `sceptre-diff-<account_name>-<region>.sh` is created. You can run this file to validate that there's no difference from the templates+config fetched and the live stacks.

## Removing NX1/Citadel Permissions

To remove external permissions, in each AWS Account, go to IAM and delete the following IAM Roles:
* `CitadelAccess-<random_id>` (or `CitadelAccess`)
* `CitadelAccessReadOnly-<random_id>` (or `CitadelAccessReadOnly`)

Do not remove the `citadel-access-*` stack as it contains CloudFormation roles used by the stacks that are currently deployed in the account.

## Clean up StackSets (optional)

Some Cloudformation stacks were created by StackSets.

Since Sceptre will manage the stacks directly, you can delete the StackSets safely, while keeping the stacks.

To do so:
* Go to Cloudformation
* Click StackSets

For each StackSet with the name starting with `citadel-*`:
* Click Actions -> Delete Stacks from StackSet
* Account Numbers: `<enter current AWS Account ID only>`
* Specify Region: `<select current AWS Region>`
* Retain stacks: YES - make sure this parameter is toggled ON, otherwise it will delete the stack.
* (Leave the other parameters untouched)
* Click Next, Submit.

This will remove the link to the stack (you can check under Stack instances).

Next we need to delete the StackSet:
* Click Actions -> Delete StackSet
* Confirm.

## Moving Forward

After all AWS Accounts are ejected, you will have a complete infrastructure-as-code repository ready to be maintained using Sceptre.

Check Sceptre documentation on how to update stacks from here. Commands will be similar to the `sceptre-diff-*.sh` file created and they can be added to a pipeline for automating infrastructure deployment.