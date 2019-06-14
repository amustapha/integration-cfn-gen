import pathlib

from setuptools import setup, find_packages

NAME = 'cirrostratus'

# Sets __version__
exec((pathlib.Path(NAME) / 'version.py').read_text())

setup(
    name=NAME,
    version=__version__,  # noqa
    description='Generate CloudFormation for BriteCore Gen 3 Integrations',
    packages=[p for p in find_packages() if not p.endswith('tests')],
    install_requires=[
        'troposphere~=2.4.7',
        'awacs~=0.9.2',
    ],
)
