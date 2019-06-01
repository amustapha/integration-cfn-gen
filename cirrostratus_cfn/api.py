from typing import Iterable

from troposphere import ImportValue, Sub, GetAtt
from troposphere.cloudformation import AWSCustomObject

from .common import Config


class APIContribution(AWSCustomObject):
    resource_type = 'Custom::ApiContribution'

    props = dict(
        ServiceToken=(str, True),
        LambdaProxyArn=(str, True),
        S3Bucket=(str, True),
        S3Key=(str, True),
    )


def resources(config: Config) -> Iterable[APIContribution]:
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
