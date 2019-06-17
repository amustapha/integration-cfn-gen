import warnings
from typing import Iterable


from troposphere import AWSObject
from troposphere import Sub, ImportValue, Ref, GetAtt
from troposphere.cloudformation import AWSCustomObject
from troposphere import awslambda as awsλ
from troposphere import iam
import awacs.awslambda
import awacs.sts
import yaml

from . import policy, secret
from .common import Config


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
        Handler=(config.LAMBDA_HANDLER or
                 f'{config.PROJECT_NAME.lower()}.awslambda.handler'),
        Runtime=f'python{config.PYTHON_VERSION}',
        Timeout=30,
        MemorySize=1024,
        TracingConfig=awsλ.TracingConfig(Mode='Active'),
        Environment=awsλ.Environment(
            Variables=dict(
                DEPLOYMENT_STAGE=Ref('Stage'),
                FLASK_ENV='production',
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
            policy.AWSLambdaBasicExecutionRole.JSONrepr(),
            policy.AWSXRayDaemonWriteAccess.JSONrepr(),
        ],
        Policies=[secret.policy(config)],
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
