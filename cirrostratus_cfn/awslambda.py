from typing import Iterable, Union

from .common import Config, Transform
from . import policy

from troposphere import AWSObject, Sub, ImportValue, Ref, GetAtt
from troposphere.cloudformation import AWSCustomObject
from troposphere import awslambda as awsλ, iam, serverless
import awacs.awslambda
import awacs.sts


class APIContribution(AWSCustomObject):
    resource_type = 'Custom::ApiContribution'

    props = dict(
        ServiceToken=(str, True),
        LambdaProxyArn=(str, True),
        S3Bucket=(str, True),
        S3Key=(str, True),
    )


def items(config: Config) -> Iterable[Union[AWSObject, Transform]]:
    yield Transform('AWS::Serverless-2016-10-31')
    yield serverless.Function(
        'ApiLambdaFunc',
        FunctionName=Sub(f'{config.PROJECT_NAME}-API-${{Stage}}'),
        CodeUri='.',
        Handler=f'{config.PACKAGE_NAME}.awslambda.handler',
        Runtime='python3.7',
        Timeout=30,
        MemorySize=1024,
        Tracing='Active',
        VpcConfig=awsλ.VPCConfig(
            SecurityGroupIds=ImportValue(Sub('${Stage}-RDSSecurityGroup')),
            SubnetIds=ImportValue(Sub('${Stage}-PrivateSubnets')),
        ),
        Environment=awsλ.Environment(
            Variables=dict(
                DEPLOYMENT_STAGE=Ref('Stage'),
                AWS_STOREAGE_BUCKET_NAME=Ref('StorageBucket'),
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
    yield APIContribution(
        'BriteApiContribution',
        Version='1.0',
        ServiceToken=ImportValue(Sub('${Stage}-ApiContribution-Provider')),
        LambdaProxyArn=GetAtt('ApiLambdaFunc', 'Arn'),
        S3Bucket=config.S3_BUCKET,
        S3Key='/'.join([config.PACKAGE_NAME,
                        'build',
                        config.SOURCE_VERSION,
                        'openapi.yaml']),
    )
