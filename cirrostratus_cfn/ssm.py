from typing import Iterable

from troposphere import Sub, Ref
from troposphere.ssm import Parameter

from .common import Config


def resources(config: Config) -> Iterable[Parameter]:
    yield Parameter(
        'Secret1Parameter',
        Type='String',
        Name=Sub(f'/${{Stage}}/{config.PACKAGE_NAME}/secret1'),
        Value=Ref('Secret1'),
        Description='Placeholder secret.',
    )
