import pathlib
import sys
from contextlib import contextmanager
from typing import List, NamedTuple


class SecretDefinition(NamedTuple):
    name: str
    description: str
    default: str


class Config(NamedTuple):
    PROJECT_NAME: str
    OPENAPI_FILE: str
    LAMBDA_HANDLER: str
    SECRETS: List[SecretDefinition]
    PYTHON_VERSION: str = '3.7'

    @contextmanager
    def openapi(self):
        if self.OPENAPI_FILE == '-':
            yield sys.stdin
            return
        with pathlib.Path(self.OPENAPI_FILE).open('r') as f:
            yield f
