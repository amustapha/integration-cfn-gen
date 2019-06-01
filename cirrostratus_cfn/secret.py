from typing import Iterable

from troposphere import Sub
from troposphere.secretsmanager import Secret

from .common import Config


def resources(config: Config) -> Iterable[Secret]:
    yield Secret(
        f'{config.PROJECT_NAME}AccountSecret',
        Name=Sub(f'${{Stage}}/{config.PACKAGE_NAME}/account_settings'),
        SecretString=Sub('"${Secret1}"'),
        Description=f'{config.PROJECT_NAME} account secret settings JSON',
    )
