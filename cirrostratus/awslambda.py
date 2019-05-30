import logging

from apig_wsgi import make_lambda_handler
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import xray_recorder
from bc_lambda import bc_lambda
import cirrostratus

_app = cirrostratus.create_app()

xray_recorder.configure(service='Cirrostratus')
XRayMiddleware(_app, xray_recorder)

_decorator = bc_lambda(level=logging.INFO, service='Cirrostratus')
handler = _decorator(make_lambda_handler(_app))
