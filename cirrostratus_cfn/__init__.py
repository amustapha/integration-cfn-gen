from typing import Iterable, Union

from troposphere import Template, AWSObject, Parameter

from cirrostratus_cfn.common import Config
from . import parameters, s3, awslambda, secret


def items(config: Config) -> Iterable[Union[AWSObject, Parameter]]:
    for mod in {parameters, s3, awslambda, secret}:
        yield from mod.items(config)


def template(config: Config) -> Template:
    t = Template()
    t.set_version('2010-09-09')
    for i in items(config):
        if isinstance(i, Parameter):
            t.add_parameter(i)
        else:
            t.add_resource(i)
    return t


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Produce a CloudFormation Template',
    )
    parser.add_argument(dest='project_name')
    parser.add_argument('--package-name')
    parser.add_argument('--openapi-file', default='')
    args = parser.parse_args()

    config = Config(
        PROJECT_NAME=args.project_name,
        PACKAGE_NAME=args.package_name or args.project_name.lower(),
        OPENAPI_FILE=args.openapi_file,
    )
    t = template(config)
    print(t.to_yaml())
