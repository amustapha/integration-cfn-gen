from typing import Iterable

from troposphere import Template, Parameter, AWSObject

from cirrostratus_cfn.common import Config
from . import s3, awslambda, api, secret, ssm


def parameters(config: Config) -> Iterable[Parameter]:
    yield Parameter(
        'Stage',
        Type='String',
        Description='The State to which to deploy Resources',
        Default='dev',
    )
    yield Parameter(
        'Secret1',
        Type='String',
        Description='A placeholder secret',
        NoEcho=True,
        Default='SETEC Astronomy',
    )


def resources(config: Config) -> Iterable[AWSObject]:
    yield from s3.resources(config)
    yield from awslambda.resources(config)
    yield from api.resources(config)
    yield from secret.resources(config)
    yield from ssm.resources(config)


def template(config: Config) -> Template:
    t = Template()
    t.set_version('2010-09-09')
    for p in parameters(config):
        t.add_parameter(p)
    for r in resources(config):
        t.add_resource(r)
    return t


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Produce a CloudFormation Template',
    )
    parser.add_argument(dest='project_name')
    parser.add_argument('--package-name')
    parser.add_argument('--source-version', default='')
    parser.add_argument('--s3-bucket', default='')
    args = parser.parse_args()

    config = Config(
        PROJECT_NAME=args.project_name,
        PACKAGE_NAME=args.package_name or args.project_name.lower(),
        SOURCE_VERSION=args.source_version,
        S3_BUCKET=args.s3_bucket,
    )
    t = template(config)
    print(t.to_yaml())
