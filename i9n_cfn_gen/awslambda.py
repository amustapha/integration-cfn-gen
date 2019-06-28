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

    @classmethod
    def make(cls, config: Config, role: iam.Role) -> 'PackagedFunction':
        kwargs = dict(
            FunctionName=Ref('AWS::StackName'),
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
            Role=GetAtt(role, 'Arn'),
        )
        if config.NAT_GATEWAY:
            kwargs['VpcConfig'] = awsλ.VPCConfig(
                SubnetIds=[Ref('NatPrivSubnet')],
                SecurityGroupIds=[Ref('NatSecurityGroup')])
        return cls(
            'ApiLambdaFunc',
            **kwargs,
        )


def make_role(config: Config) -> iam.Role:
    kwargs = dict(
        AssumeRolePolicyDocument=policy.AllowAssumeRole,
        ManagedPolicyArns=[
            policy.AWSLambdaBasicExecutionRole.JSONrepr(),
            policy.AWSXRayDaemonWriteAccess.JSONrepr(),
        ],
    )
    if config.SECRETS:
        kwargs['Policies'] = [secret.policy(config)]
    if config.NAT_GATEWAY:
        kwargs['ManagedPolicyArns'].append(
            policy.AWSLambdaVPCAccessExecutionRole.JSONrepr())
    return iam.Role('LambdaRole', **kwargs)


def items(config: Config) -> Iterable[AWSObject]:
    role = make_role(config)
    yield role
    func = PackagedFunction.make(config, role)
    yield func

    if config.OPENAPI_FILE:
        yield awsλ.Permission(
            'LambdaInvokePermission',
            FunctionName=Ref(func),
            Principal='apigateway.amazonaws.com',
            Action=awacs.awslambda.InvokeFunction.JSONrepr(),
        )
        with config.openapi() as f:
            openapi_data = yaml.safe_load(f)
        yield APIContribution(
            'BriteApiContribution',
            Version='1.0',
            ServiceToken=ImportValue(Sub('${Stage}-ApiContribution-Provider')),
            LambdaProxyArn=GetAtt(func, 'Arn'),
            RestApiId=ImportValue(Sub('${Stage}-BriteAPI')),
            SwaggerDefinition=openapi_data,
        )
    else:
        warnings.warn('No OpenAPI file passed; not emitting BriteAPI')
