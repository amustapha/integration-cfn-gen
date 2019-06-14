"""
This is a barebones example plugin module.

All of the type annotations are just for clarification and are optional.

Your function that you define on the command line resides in here. It takes a
cirrostratus Config object and then you may generate or return a list of
Troposphere objects. Any objects for any purpose may be output.

To use, simply make sure it's importable in Python and use the flag
--plugin module:function on the command line.
"""

from typing import Iterable

from troposphere.s3 import Bucket

from cirrostratus.common import Config  # noqa: F401


def bucket(config: 'Config') -> Iterable:
    yield Bucket('PrivateBucket')
