from flask import request, Blueprint, Response
from gatekeeper.app import app
from gatekeeper.dependencies.deed_api import DeedApi
import json
import os
import sys
from jsonschema.validators import validator_for
from underscore import _
import collections

# This is the blueprint object that gets registered into the app in blueprints.py.
deed_gatekeeper = Blueprint('deed_gatekeeper', __name__)


@deed_gatekeeper.route("/health", methods=['GET'])
def check_status():
    deed = DeedApi()
    app.logger.info('Calling get health dependency')
    resp = deed.health()
    log_call_result('get health', resp, 200)

    return build_response(resp)


@deed_gatekeeper.route("/<deed_reference>", methods=['GET'])
def get_deed(deed_reference):
    deed = DeedApi()
    app.logger.info('Calling get deed dependency')
    resp = deed.get_deed(deed_reference, request.headers)
    log_call_result('get deed', resp, 200)

    return build_response(resp)


@deed_gatekeeper.route("/dashboard/<status>", methods=['GET'])
def get_metrics(status):
    deed = DeedApi()
    app.logger.info('Calling get metrics dependency')
    resp = deed.get_metrics(status, request.headers)
    log_call_result('get metrics', resp, 200)

    return build_response(resp)


@deed_gatekeeper.route("/", methods=['POST'])
def create_deed():
    deed = DeedApi()
    payload = request.get_json()

    app.logger.info('Validating schema')
    schema_check = validate_schema(payload)

    if schema_check:
        app.logger.error('Schema check failed')
        return Response(response=json.dumps({"errors": schema_check}), mimetype='application/json', status=400)

    app.logger.info('Making call to create deed dependency')
    resp = deed.create_deed(payload, request.headers)
    log_call_result('create deed', resp, 201)

    return build_response(resp)


@deed_gatekeeper.route("/<deed_reference>/make-effective", methods=['POST'])
def make_effective(deed_reference):
    deed = DeedApi()

    app.logger.info('Making call to update deed dependency')
    resp = deed.make_effective(deed_reference, request.headers)
    log_call_result('make effective', resp, 200)

    return build_response(resp)


@deed_gatekeeper.route("/retrieve-signed", methods=['GET'])
def retrieve_signed():
    deed = DeedApi()

    app.logger.info('Making call to update deed dependency')
    resp = deed.retrieve_signed(request.headers)
    log_call_result('retrieve signed', resp, 200)

    return build_response(resp)


def build_response(resp):
    app.logger.info('Building API response')

    body = None
    mime_type = None

    if resp.text:
        if 'text/html; charset=utf-8' in resp.headers.get("content-type", ""):
            body = resp.text
            mime_type = "text/html"
        else:
            body = json.dumps(resp.json())
            mime_type = "application/json"
    test = Response(response=body, mimetype=mime_type, status=resp.status_code)
    return test


def call_once_only(func):
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result
    return decorated


@call_once_only
def get_swagger_file():
    dirname = os.path.dirname(os.path.abspath(__file__))
    return load_json_file(dirname +
                          "/deed-api.json")


def load_json_schema():
    swagger = get_swagger_file()

    definitions = swagger["definitions"]
    deed_application_definition = definitions["Deed_Application"]

    deed_application = {
        "definitions": definitions,
        "properties": deed_application_definition["properties"],
        "required": deed_application_definition["required"],
        "type": "object",
        "additionalProperties": False
    }

    return deed_application


def _create_title_validator():
    schema = load_json_schema()
    validator = validator_for(schema)
    validator.check_schema(schema)
    return validator(schema)


def load_json_file(file_path):
    with open(file_path, 'rt', encoding='utf-8') as file:
        json_data = json.load(file)

    return json_data


def validator(payload):
    _title_validator = _create_title_validator()
    schema_errors = []
    error_list = sorted(_title_validator.iter_errors(payload),
                        key=str, reverse=True)

    for error in enumerate(error_list, start=1):
        schema_errors.append(str(error))

    return schema_errors


# schema is a json obj/dict
# path - contains the string path to a dict attribute
# with '/' separators e.g. /root/sub_ele/child1/attr_name
def get_obj_by_path(schema, path):

    def down_one_level(schema, key, context):
        try:
            res = schema[key]
            return res
        except Exception:
            app.logger.error(
                "ACCESS ERROR:\nlocation in schema: %s\n with key: %s \n%s."
                % (schema, key, sys.exc_info()[0]))
            raise

    return _.reduce(path.strip("/").split("/"), down_one_level, schema)


def validate_schema(payload):
    _title_validator = _create_title_validator()
    error_message = []
    error_list = sorted(_title_validator.iter_errors(payload),
                        key=str, reverse=True)

    ids = []
    for borrower in payload["borrowers"]:
        if 'id' in borrower:
            ids.append(borrower['id'])

    duplicates = [item for item, count in collections.Counter(ids).items() if count > 1]
    if duplicates:
        error_list.append("A borrower ID must be unique to an individual.")

    for count, error in enumerate(error_list, start=1):
        error_message.append("Problem %s: %s" % (count, str(error)))

    return error_message


def log_call_result(dependency, response, status_code):
    app.logger.info('Call to %s has been successful.', dependency) if response.status_code == status_code \
        else app.logger.error('Call to %s has failed.', dependency)
