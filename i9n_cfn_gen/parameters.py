from typing import Iterable

from troposphere import Parameter

from .common import Config


def items(config: Config) -> Iterable[Parameter]:
    yield Parameter(
        'Stage',
        Type='String',
        Description='The Stage to which to deploy Resources',
        Default='dev')
