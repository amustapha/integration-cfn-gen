import importlib
from typing import List, Iterable, Union

from troposphere import Template, AWSObject, Parameter, Output

from .common import Config, SecretDefinition
from .version import __version__  # noqa: F401


Item = Union[AWSObject, Parameter, Output]
BUILTIN_PLUGINS = ['i9n_cfn_gen.parameters:items',
                   'i9n_cfn_gen.awslambda:items',
                   'i9n_cfn_gen.secret:items',
                   'i9n_cfn_gen.nat_gateway:items']


def plug(config: Config, plugin_path: str) -> Iterable[Item]:
    module_path, function_name = plugin_path.split(':')
    module = importlib.import_module(module_path)
    function = getattr(module, function_name)
    yield from function(config)


def items(config: Config, plugins: List[str]) -> Iterable[Item]:
    for plugin_path in BUILTIN_PLUGINS + plugins:
        yield from plug(config, plugin_path)


def template(config: Config, plugins: List[str]) -> Template:
    t = Template()
    t.set_version('2010-09-09')
    for i in items(config, plugins):
        if isinstance(i, Parameter):
            t.add_parameter(i)
        elif isinstance(i, Output):
            t.add_output(i)
        else:
            t.add_resource(i)
    return t


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Produce a CloudFormation Template',
    )
    parser.add_argument(
        dest='project_name',
        metavar='PROJECT_NAME')
    parser.add_argument(
        '--lambda-handler',
        default=None,
        metavar='package.module.function',
        help='defaults to lowercase of project_name.awslambda.handler')
    parser.add_argument(
        '--openapi-file',
        default=None,
        help='path to OpenAPI YAML to add to API Gateway')
    parser.add_argument(
        '--secret',
        nargs=3,
        action='append',
        dest='secrets',
        metavar=('NAME', 'DESCRIPTION', 'DEFAULT'),
        default=[],
        help=('define a secret parameter, multiples allowed. '
              'If no default, use empty string "".'))
    parser.add_argument(
        '--plugin',
        action='append',
        dest='plugins',
        metavar='package.module:function',
        help='Python function yields Troposphere objects to add to template')
    parser.add_argument(
        '--python',
        default='3.7',
        help='Python version to deploy.',
    )
    parser.add_argument(
        '--nat-gateway',
        action='store_true',
        help='Use a VPC and a NAT gateway so function has fixed IP',
    )
    args = parser.parse_args()

    config = Config(
        PROJECT_NAME=args.project_name,
        LAMBDA_HANDLER=args.lambda_handler,
        OPENAPI_FILE=args.openapi_file,
        SECRETS=[SecretDefinition(*s) for s in args.secrets],
        PYTHON_VERSION=args.python,
        NAT_GATEWAY=args.nat_gateway,
    )
    t = template(config, args.plugins or [])
    print(t.to_yaml())
