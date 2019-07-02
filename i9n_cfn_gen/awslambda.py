import warnings
from typing import Iterable, Tuple

from troposphere import AWSObject, Tags
from troposphere import Sub, ImportValue, Ref, GetAtt, Split
from troposphere.cloudformation import AWSCustomObject
from troposphere import awslambda as awsλ, iam, ec2
import awacs.awslambda
import awacs.sts
import yaml

from . import policy, secret
from .common import Config


VPC = ImportValue(Sub('${Stage}-VPC'))
PUBLIC_SUBNETS = Split(',', ImportValue(Sub('${Stage}-PublicSubnets')))
PRIVATE_SUBNETS = Split(',', ImportValue(Sub('${Stage}-PrivateSubnets')))


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
    def make(cls, config: Config, role: iam.Role
             ) -> Tuple['PackagedFunction', ec2.SecurityGroup]:
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
                    STACK_NAME=Ref('AWS::StackName'),
                    DEPLOYMENT_STAGE=Ref('Stage'),
                    FLASK_ENV='production',
                ),
            ),
            Role=GetAtt(role, 'Arn'),
        )
        sg = None
        if config.NAT_GATEWAY:
            sg = ec2.SecurityGroup(
                'EgressSecurityGroup',
                Tags=Tags(Name=Sub('${AWS::StackName}-lambda-functions')),
                GroupDescription='Egress Only',
                VpcId=VPC)
            kwargs['VpcConfig'] = awsλ.VPCConfig(
                SubnetIds=PRIVATE_SUBNETS,
                SecurityGroupIds=[Ref(sg)])
        return cls('ApiLambdaFunc', **kwargs), sg


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
    func, sg = PackagedFunction.make(config, role)
    yield func
    if sg:
        yield sg

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
