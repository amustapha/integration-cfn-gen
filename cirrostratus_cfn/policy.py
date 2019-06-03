from typing import Iterable

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

from .common import Config

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


def allow_get_secrets(config: Config, secret_names: Iterable[str]) -> Policy:
    return Policy(
        'AllowGetAccountSecret',
        PolicyName='AllowGetAccountSecret',
        PolicyDocument=PolicyDocument(
            Statement=[
                Statement(
                    Action=[awacs.secretsmanager.GetSecretValue],
                    Effect=Allow,
                    Resource=[
                        Sub(f'${{{config.PROJECT_NAME}{n}Secret}}*')
                        for n in secret_names
                    ],
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
