from flask import Blueprint
import json
from gatekeeper.app import app

exceptions = Blueprint('exceptions', __name__)


@exceptions.app_errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e,), exc_info=True)
    return json.dumps({"message": "Unexpected error."}), 500
