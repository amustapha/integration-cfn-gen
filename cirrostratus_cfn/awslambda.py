from typing import Iterable

from .common import Config
from . import policies

from troposphere import AWSObject, Sub, ImportValue, Ref, GetAtt
from troposphere import awslambda as awsλ
from troposphere import iam
import awacs.awslambda
import awacs.sts


def resources(config: Config) -> Iterable[AWSObject]:
    yield awsλ.Function(
        'ApiLambdaFunc',
        FunctionName=Sub(f'{config.PROJECT_NAME}-API-${{Stage}}'),
        Code=awsλ.Code(ZipFile='./'),
        Handler=f'{config.PACKAGE_NAME}.awslambda.handler',
        Runtime='python3.7',
        Timeout=30,
        MemorySize=1024,
        TracingConfig=awsλ.TracingConfig(Mode='Active'),
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
        AssumeRolePolicyDocument=policies.AllowAssumeRole,
        ManagedPolicyArns=[
            policies.AWSLambdaVPCAccessExecutionRole.JSONrepr(),
            policies.AWSLambdaBasicExecutionRole.JSONrepr(),
            policies.AWSXRayDaemonWriteAccess.JSONrepr(),
        ],
        Policies=[
            policies.allow_get_account_secret(config),
            policies.allow_get_ssm_params(config),
        ],
    )
