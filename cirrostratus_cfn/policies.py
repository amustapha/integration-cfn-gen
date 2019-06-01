from .common import Config

from troposphere import Sub
from troposphere.iam import Policy
from awacs.aws import (PolicyDocument, Statement,
                       Principal, Allow)
import awacs.aws
import awacs.awslambda
import awacs.secretsmanager
import awacs.ssm
import awacs.sts
import awacs.iam


AWSLambdaVPCAccessExecutionRole = awacs.iam.ARN(
    'policy/service-role/AWSLambdaVPCAccessExecutionRole',
    account='aws',
)
AWSLambdaBasicExecutionRole = awacs.iam.ARN(
    'policy/service-role/AWSLambdaBasicExecutionRole',
    account='aws',
)
AWSXRayDaemonWriteAccess = awacs.iam.ARN(
    'policy/AWSXRayDaemonWriteAccess',
    account='aws',
)
AllowAssumeRole = awacs.aws.Policy(
    Statement=[
        Statement(
            Action=[awacs.sts.AssumeRole],
            Effect=Allow,
            Principal=Principal(
                'Service',
                ['lambda.amazonaws.com',
                 'events.amazonaws.com']
            )
        ),
    ]
)


def allow_get_account_secret(config: Config) -> Policy:
    return Policy(
        'AllowGetAccountSecret',
        PolicyName='AllowGetAccountSecret',
        PolicyDocument=PolicyDocument(
            Statement=[
                Statement(
                    Action=[awacs.secretsmanager.GetSecretValue],
                    Effect=Allow,
                    Resource=[Sub(f'${{{config.PROJECT_NAME}'
                                  f'AccountSecret}}*')],
                )
            ]
        )
    )


def allow_get_ssm_params(config: Config) -> Policy:
    return Policy(
        'AllowGetSSMParams',
        PolicyName='AllowGetSSMParams',
        PolicyDocument=PolicyDocument(
            Statement=[
                Statement(
                    Action=[awacs.ssm.GetParameters],
                    Effect=Allow,
                    Resource=[Sub('arn:aws:ssm:${AWS::Region}:'
                                  '${AWS::AccountId}:'
                                  'parameter/${Stage}/'
                                  f'{config.PACKAGE_NAME}')],
                )
            ]
        )
    )
