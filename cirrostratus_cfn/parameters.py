from typing import Iterable

from troposphere import Parameter

from cirrostratus_cfn.common import Config


def items(config: Config) -> Iterable[Parameter]:
    yield Parameter(
        'Stage',
        Type='String',
        Description='The State to which to deploy Resources',
        Default='dev')
