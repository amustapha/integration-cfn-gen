from typing import Iterable

from troposphere.s3 import Bucket, VersioningConfiguration

from .common import Config


def items(config: Config) -> Iterable[Bucket]:
    yield Bucket(
        'StorageBucket',
        VersioningConfiguration=VersioningConfiguration(Status='Enabled'),
    )
