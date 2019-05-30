import pathlib

from setuptools import setup, find_packages

NAME = 'cirrostratus'
REQUIRES = ['flask~=1.0.3']
PROD_REQUIRES = [
    'apig-wsgi~=2.2.0',
    'aws-xray-sdk~=2.4.2',
    ('bc-lambda @ '
     'http://bc-pip-wheelhouse.s3-website-us-east-1.amazonaws.com/'
     'bc_lambda-0.6.0-py2.py3-none-any.whl'),
]
# Sets __version__
exec((pathlib.Path(NAME) / 'version.py').read_text())

setup(
    name=NAME,
    version=__version__,  # noqa
    packages=[p for p in find_packages() if not p.endswith('tests')],
    package_data={NAME: {'openapi.yaml'}},
    install_requires=REQUIRES,
    extras_require={
        'prod': PROD_REQUIRES,
    },
    description='Testbed for launching CloudFormation Lambda services',
)
