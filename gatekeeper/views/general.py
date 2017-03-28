from flask import request, Blueprint, Response, jsonify
from flask import current_app
import json
import logging
import requests

LOGGER = logging.getLogger(__name__)


# This is the blueprint object that gets registered into the app in blueprints.py.
general = Blueprint('general', __name__)


@general.route("/health")
def check_status():
    return Response(response=json.dumps({
        "app": "gatekeeper",
        "status": "OK",
        "headers": str(request.headers),
        "commit": current_app.config["COMMIT"]
    }), mimetype='application/json', status=200)


@general.route('/health/service-check')
def service_check_routes():

    # Attempt to connect to gatekeeper which will attempt to connect to all
    # other services that are related to it.
    service_list = ""

    service_dict = {
        "status_code": 500,
        "service_from": "gatekeeper",
        "service_to": "deed-api",
        "service_message": "Successfully connected"
    }

    try:
        service_response = requests.get(current_app.config["DEED_API_URL"] + '/health/service-check')

        status_code = service_response.status_code
        service_list = service_response.json()

        # Add the success json for Gatekeeper to the list of services
        # If there was an exception it would not get to this point
        service_dict["status_code"] = status_code
        service_list["services"].append(service_dict)

    except Exception as e:
        # A RequestException resolves the error that occurs when a connection cant be established
        # and the ValueError/TypeError exception may occur if the dict string / object is malformed
        LOGGER.error('An exception has occurred in the service-check endpoint: %s', (e,), exc_info=True)

        # We either have a differing status code, add an error for this service
        # This would imply that we were not able to connect to gatekeeper
        service_dict["status_code"] = 500
        service_dict["service_message"] = "Error: Could not connect"

        service_list = {
            "services":
            [
                service_dict
            ]
        }

    # Return the json object containing the status of each service
    return jsonify(service_list)
