# Rally test, DO NOT MERGE

# CloudFormation Generation Tool for Integrations

This program uses [Troposphere](https://github.com/cloudtools/troposphere) to
generate CloudFormation templates for BriteCore Generation 3 Integration
backends.

## Usage

Basic execution is with `i9n-cfn-gen ProjectName` once installed.

A few optional flags are available for the that command.

 + `--lambda-handler`: Allows you to define the Lambda function handler
   parameter. If not defined it'll be `LOWER(project_name).awslambda.handler`.
 + `--openapi-file`: An OpenAPI/Swagger file to add to the API Gateway. Can be
   `-` for standard input.
 + `--secret`: Takes three arguments: name, description, and default. These
   create a Parameter by the defined name that fills the secret with the entered
   data. A default can be provided. A default of empty string `""` will be ignored.
 + `--plugin`: Extra functionality can be defined by entering the
   `import.path:func` to a function that outputs Troposphere objects.
 + `--python`: Define the Python version to deploy. Defaults to 3.7.
 + `--nat-gateway`: Run the Lambda function in the Stage's VPC using a NAT
   Gateway with fixed IP address; e.g. for IP-whitelisted services.


## Set Up

There are files in the `example/` directory that you can copy and modify into
your project to make handy use of this project.


### Secrets

In your Lambda function, reading Secrets can be done with `boto3`.

If you've defined a secret like
`i9n-cfn-gen ProjectName --secret MySecret "Example Secret Password" "correct horse battery staple"`
you can load it in your Python app like so:

```python
import os

import boto3


DEPLOYMENT_STAGE = os.getenv('DEPLOYMENT_STAGE')
STACK_NAME = os.getenv('STACK_NAME')

secretsmanager = boto3.client('secretsmanager')
MY_SECRET = secretsmanager.get_secret_value(f'/{STACK_NAME}/MySecret')['SecretString']
```

### Plugins

You can provide extra resources in the template by way of a plugin.

If you have a file like below called `plug.py` and execute the following:
`i9n-cfn-gen ProjectName --plugin plug:stuff` it will add a Parameter
and a Bucket.

```python
from troposhere import Parameter, Sub
from troposhere.s3 import Bucket


def stuff(config):
    yield Parameter(
        'Color',
        Type='String',
        Description='What color will it be?',
        Default='blue')
    yield Bucket(
        'ColoredBucket',
        Name=Sub('my-bucket-${Color}'))
```
