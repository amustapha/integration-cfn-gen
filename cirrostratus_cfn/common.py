import dataclasses
import pathlib
import sys
from contextlib import contextmanager


@dataclasses.dataclass(frozen=True)
class Config():
    PROJECT_NAME: str
    PACKAGE_NAME: str
    OPENAPI_FILE: str

    @contextmanager
    def openapi(self):
        if self.OPENAPI_FILE == '-':
            yield sys.stdin
            return
        with pathlib.Path(self.OPENAPI_FILE).open('r') as f:
            yield f
