from typing import NamedTuple


class Config(NamedTuple):
    PROJECT_NAME: str
    PACKAGE_NAME: str
    SOURCE_VERSION: str
    S3_BUCKET: str
    OPENAPI_FILE: str
