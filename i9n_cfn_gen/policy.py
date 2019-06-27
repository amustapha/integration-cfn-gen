from typing import Iterable

from troposphere import Sub, Ref
from troposphere.iam import Policy
from awacs.aws import (PolicyDocument, Statement,
                       Principal, Allow)
import awacs.aws
import awacs.awslambda
import awacs.secretsmanager
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


def secret_path(config: Config, secret_name: str) -> Sub:
    """
    The stage-subbing path to a secret by name.
    """
    return Sub(f'/${{Stage}}/{config.PROJECT_NAME}/{secret_name}')


def allow_get_secrets(secret_names: Iterable[str]) -> Policy:
    return Policy(
        'AllowGetAccountSecrets',
        PolicyName='AllowGetAccountSecrets',
        PolicyDocument=PolicyDocument(
            Statement=[
                Statement(
                    Action=[awacs.secretsmanager.GetSecretValue],
                    Effect=Allow,
                    Resource=[Ref(f'Secret{n}') for n in secret_names],
                )
            ]
        )
    )
