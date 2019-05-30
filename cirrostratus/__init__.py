#!/usr/bin/env python
import itertools
import pathlib
import random
from typing import Iterable

import flask

from .version import VERSION as __version__, API_VERSION

ROOT_DIR = pathlib.Path(__file__).parent
OPENAPI_YAML_PATH = ROOT_DIR / 'openapi.yaml'

def create_app() -> flask.Flask:
    app = flask.Flask('cirrostratus')
    PATH_PREFIX = '/testbed/cirrostratus'

    @app.route(f'{PATH_PREFIX}/coconuts', methods=['GET'])
    def coconuts():
        """
        The sounds that a coconut makes, Monty Python style.
        """
        def gen() -> Iterable[str]:
            clippy = 'Clippy-clop!\n'
            yield from itertools.repeat(clippy, random.randint(1, 10))
            yield 'Clip-clip clop.\n'
        return flask.Response(gen(), 200, mimetype='text/plain')

    @app.route(f'{PATH_PREFIX}/echo', methods=['POST'])
    def echo():
        """
        Echo back posted request body
        """
        return flask.Response(
            flask.request.data,
            200,
            mimetype=flask.request.content_type,
        )

    @app.cli.command('openapi')
    def openapi_cmd():
        import sys
        import shutil
        with OPENAPI_YAML_PATH.open() as yamlf:
            shutil.copyfileobj(yamlf, sys.stdout)

    @app.route(f'{PATH_PREFIX}/openapi.yaml', methods=['GET'])
    def openapi_yml():
        return flask.send_file(str(OPENAPI_YAML_PATH))

    return app
