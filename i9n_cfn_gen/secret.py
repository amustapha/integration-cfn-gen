from typing import Iterable, Union, Optional, NamedTuple

from troposphere import Ref, Parameter
from troposphere.iam import Policy
from troposphere.secretsmanager import Secret

from .common import Config
from .policy import allow_get_secrets, secret_path


class SecretDef(NamedTuple):
    parameter: Parameter
    secret: Secret

    @classmethod
    def make(cls, config: Config,
             secret_name: str,
             description: str,
             default: Optional[str] = None) -> 'SecretDef':
        path = secret_path(config, secret_name)
        return cls(
            parameter=Parameter(
                secret_name,
                Type='String',
                Description=description,
                NoEcho=True,
                **({'Default': default} if default else {})),
            secret=Secret(
                f'Secret{secret_name}',
                Name=path,
                SecretString=Ref(secret_name),
                Description=description),
        )


def items(config: Config) -> Iterable[Union[Parameter, Secret]]:
    for name, desc, default in config.SECRETS:
        yield from SecretDef.make(config, name, desc, default)  # noqa: T484


def policy(config: Config) -> Policy:
    return allow_get_secrets(name for name, *_ in config.SECRETS)
