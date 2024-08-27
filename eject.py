import boto3
import os
import yaml
from pprint import pprint
import argparse

# Create an argument parser
parser = argparse.ArgumentParser(description='Script to fetch and save CloudFormation stack information')

# Add the region argument
parser.add_argument('--region', help='AWS region', required=True)
parser.add_argument('--account-name', help='AWS account name', required=True)

# Parse the arguments
args = parser.parse_args()

# Assign the region value
region = args.region
account_name = args.account_name

stack_name_prefixes = ['StackSet-citadel-', 'citadel-']
stack_files = []

# Create a CloudFormation client
cloudformation = boto3.client('cloudformation', region_name=region)

# List all stacks
response = cloudformation.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE'])

# Filter stacks by name prefix
filtered_stacks = [stack for stack in response['StackSummaries'] if stack['StackName'].startswith(tuple(stack_name_prefixes))]

# Define the output folder path
output_folder = f"config/{account_name}/{region}"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Write the sceptre config to the output file with the region
with open(f"{output_folder}/config.yaml", 'w') as file:
  yaml.dump({'region': region}, file)

# Iterate over the filtered stacks
for stack in filtered_stacks:

  # Get the stack name
  stack_name = stack['StackName']
  
  # Get the IAM role name
  
  # Get the stack parameters
  response = cloudformation.describe_stacks(StackName=stack_name)
  iam_role_arn = response['Stacks'][0]['RoleARN'] if 'RoleARN' in response['Stacks'][0] else None
  stack_parameters = response['Stacks'][0]['Parameters'] if 'Parameters' in response['Stacks'][0] else []
  
  # Create the output file path
  output_file = f"{output_folder}/{stack_name}.yaml"
  
  # Create the template folder path
  template_folder = f"templates/{account_name}/{region}"

  # Create the template folder if it doesn't exist
  os.makedirs(template_folder, exist_ok=True)

  # Fetch the template
  response = cloudformation.get_template(StackName=stack_name)
  template_body = response['TemplateBody']

  # Create the template file path
  template_file = f"{template_folder}/{stack_name}.yaml"

  # Write the template to the template file
  with open(template_file, 'w') as file:
    file.write(template_body)

  # Create the stack information dictionary
  stack_info = {
    'template': {
    'type': 'file',
    'path': template_file.replace('templates/', '')
    },
    'stack_name': stack_name,
    'parameters': {param['ParameterKey']: param['ParameterValue'] for param in stack_parameters}
  }

  if iam_role_arn:
    stack_info['cloudformation_service_role'] = iam_role_arn

  # Write the stack information to the output file
  with open(output_file, 'w') as file:
    yaml.dump(stack_info, file)

  # Write sceptre commands for each stack
  stack_files.append(f"{account_name}/{region}/{stack_name}.yaml")

# Write the sceptre commands to the sceptre file
with open(f"sceptre-diff-{account_name}-{region}.sh", 'w') as file:
  file.write(f"# {account_name} - {region}\n")
  for stack_file in stack_files:
    file.write(f"sceptre diff {stack_file}\n")

print(f"Run sceptre-diff-{account_name}-{region}.sh to see the differences between the local and remote stacks")