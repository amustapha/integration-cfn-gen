import pathlib
import sys
import warnings
from typing import Iterable


from troposphere import AWSObject
from troposphere import Sub, ImportValue, Ref, GetAtt, Split
from troposphere.cloudformation import AWSCustomObject
from troposphere import awslambda as awsλ
from troposphere import iam
import awacs.awslambda
import awacs.sts
import yaml

from .common import Config
from . import policy


class APIContribution(AWSCustomObject):
    resource_type = 'Custom::ApiContribution'

    props = dict(
        ServiceToken=(str, True),
        LambdaProxyArn=(str, True),
        S3Bucket=(str, False),
        S3Key=(str, False),
        SwaggerDefinition=(dict, False),
        RestApiId=(str, False),
    )


class PackagedCode(str):
    '''
    For use with `aws cloudformation package`.

    Used in place of awsλ.Code, output as a string that is the path to the
    code bundle to package.
    '''


class PackagedFunction(awsλ.Function):
    '''
    A normal Lambda Function but has "Code" parameter as a string, for use with
    `aws cloudformation package` tool.
    '''
    props = awsλ.Function.props.copy()
    props['Code'] = (PackagedCode, True)


def items(config: Config) -> Iterable[AWSObject]:
    yield PackagedFunction(
        'ApiLambdaFunc',
        FunctionName=Sub(f'${{Stage}}-{config.PROJECT_NAME}-API'),
        Code=PackagedCode('.'),
        Handler=f'{config.PACKAGE_NAME}.awslambda.handler',
        Runtime='python3.7',
        Timeout=30,
        MemorySize=1024,
        TracingConfig=awsλ.TracingConfig(Mode='Active'),
        VpcConfig=awsλ.VPCConfig(
            SecurityGroupIds=[ImportValue(Sub('${Stage}-RDSSecurityGroup'))],
            SubnetIds=Split(',', ImportValue(Sub('${Stage}-PrivateSubnets'))),
        ),
        Environment=awsλ.Environment(
            Variables=dict(
                DEPLOYMENT_STAGE=Ref('Stage'),
                # AWS_STORAGE_BUCKET_NAME=Ref('StorageBucket'),
                FLASK_ENV='production',
                FLASK_APP=config.PACKAGE_NAME,
            ),
        ),
        Role=GetAtt('LambdaRole', 'Arn'),
    )

    yield awsλ.Permission(
        'LambdaInvokePermission',
        FunctionName=Ref('ApiLambdaFunc'),
        Principal='apigateway.amazonaws.com',
        Action=awacs.awslambda.InvokeFunction.JSONrepr(),
    )

    yield iam.Role(
        'LambdaRole',
        AssumeRolePolicyDocument=policy.AllowAssumeRole,
        ManagedPolicyArns=[
            policy.AWSLambdaVPCAccessExecutionRole.JSONrepr(),
            policy.AWSLambdaBasicExecutionRole.JSONrepr(),
            policy.AWSXRayDaemonWriteAccess.JSONrepr(),
        ],
        Policies=[
            policy.allow_get_secrets(config, ['Secret1']),
            policy.allow_get_ssm_params(config),
        ],
    )
    if config.OPENAPI_FILE:
        with config.openapi() as f:
            openapi_data = yaml.safe_load(f)
        yield APIContribution(
            'BriteApiContribution',
            Version='1.0',
            ServiceToken=ImportValue(Sub('${Stage}-ApiContribution-Provider')),
            LambdaProxyArn=GetAtt('ApiLambdaFunc', 'Arn'),
            RestApiId=ImportValue(Sub('${Stage}-BriteAPI')),
            SwaggerDefinition=openapi_data,
        )
    else:
        warnings.warn('No OpenAPI file passed; not emitting BriteAPI')
