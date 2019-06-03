from typing import Iterable, Union, Optional

from troposphere import Ref, Sub, Parameter as CfnParameter
from troposphere.secretsmanager import Secret
from troposphere.ssm import Parameter as SsmParameter

from .common import Config


SecretThing = Union[Secret, CfnParameter, SsmParameter]


def items(config: Config) -> Iterable[SecretThing]:
    yield from secret(
        'Secret1',
        'A placeholder secret',
        config,
        default='SETEC Astronomy')


def secret(name: str, description: str, config: Config,
           default: Optional[str] = None
           ) -> Iterable[Union[CfnParameter, SsmParameter, Secret]]:
    stage_name = Sub(f'${{Stage}}/{config.PACKAGE_NAME}/{name}')
    yield CfnParameter(
        name,
        Type='String',
        Description=description,
        NoEcho=True,
        Default=default)
    yield SsmParameter(
        f'{config.PROJECT_NAME}{name}Parameter',
        Type='String',
        Name=stage_name,
        Value=Ref(name),
        Description=description)
    yield Secret(
        f'{config.PROJECT_NAME}{name}Secret',
        Name=stage_name,
        SecretString=Ref(name),
        Description=description)
