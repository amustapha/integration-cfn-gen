import pathlib

from setuptools import setup

NAME = 'i9n_cfn_gen'
README = pathlib.Path('README.md').read_text()

# Sets __version__
exec((pathlib.Path(NAME) / 'version.py').read_text())

setup(
    name=NAME,
    version=__version__,  # noqa
    description='Generate CloudFormation for BriteCore Gen 3 Integrations',
    packages=[NAME],
    install_requires=[
        'troposphere~=2.4.7',
        'awacs~=0.9.2',
    ],
    python_requires='>=3.6.0',
    entry_points=dict(
        console_scripts=['i9n-cfn-gen = i9n_cfn_gen:main'],
    ),
    long_description=README,
    long_description_content_type='text/markdown',
    keywords='BriteCore Gen3 DevOps AWS CloudFormation',
    author='Joshua Gardner',
    author_email='jgardner@wcf.com',
)
