import logging

from apig_wsgi import make_lambda_handler
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import xray_recorder
from bc_lambda import bc_lambda

import project

_app = project.create_app()

xray_recorder.configure(service='ProjectName')
XRayMiddleware(_app, xray_recorder)

_decorator = bc_lambda(level=logging.INFO, service='ProjectName')
handler = _decorator(make_lambda_handler(_app))
