import datetime
from flask import request, Blueprint, Response, jsonify, current_app, g
from gatekeeper.app import app
import json
import requests


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
        "audit_api_status_code": 500,
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

        # Check the response for audit-api and add it to the return
        service_response = requests.get(current_app.config["AUDIT_API_URI"] + '/health')
        service_dict["audit_api_status_code"] = service_response.status_code

    except Exception as e:
        # A RequestException resolves the error that occurs when a connection cant be established
        # and the ValueError/TypeError exception may occur if the dict string / object is malformed
        app.logger.error('An exception has occurred in the service-check endpoint: %s', (e,), exc_info=True)

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


@general.route("/health/cascade/<str_depth>")
def cascade_health(str_depth):
    depth = int(str_depth)

    if (depth < 0) or (depth > int(current_app.config.get("MAX_HEALTH_CASCADE"))):
        current_app.logger.error("Cascade depth {} out of allowed range (0 - {})"
                                 .format(depth, current_app.config.get("MAX_HEALTH_CASCADE")))
        return Response(response=json.dumps({
            "app": current_app.config.get("APP_NAME"),
            "cascade_depth": str_depth,
            "status": "ERROR",
            "timestamp": str(datetime.datetime.now())
        }), mimetype='application/json', status=500)
    dbs = []
    services = []
    overall_status = 200  # if we encounter a failure at any point then this will be set to != 200
    if current_app.config.get("DEPENDENCIES") is not None:
        for dependency, value in current_app.config.get("DEPENDENCIES").items():
            # Below is an example of hitting a database dependency - in this instance postgresql
            # It requires a route to obtain the current timestamp to be declared somewhere in code
            # In the below example we have an sql.py script containing the get_current_timestamp() function
            # if "postgres" in value:
            #    # postgres db url - try calling current timestamp routine
            #    db = {}
            #    db["name"] = dependency
            #    try:
            #        db_timestamp = db_timestamp = postgres.get_current_timestamp()
            #        # trim microseconds to 3 to match java
            #        db["current_timestamp"] = db_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
            #        db["status"] = "OK"
            #    except Exception as e:
            #        current_app.logger.error("Unknown error occured during health cascade on request to database: {};"
            #                                 " full error: {}.".format(dependency, e))
            #        overall_status = 500
            #        db["status"] = "BAD"
            #    finally:
            #        dbs.append(db)
            # else:  # indent the following code to match the if..else block when database checks are included
            if depth > 0:
                # As there is an inconsistant approach to url variables we need to check
                # to see if we have a trailing '/' and add one if not
                if value[-1] != '/':
                    value = value + '/'
                # Setup our service entry
                service = {
                    "name": dependency,
                    "type": "http"
                }
                try:
                    resp = g.requests.get(value + 'health/cascade/' + str(depth - 1))  # Try and request the health
                except ConnectionAbortedError as e:  # More specific logging statement for abortion error
                    current_app.logger.error("Connection Aborted during health cascade on attempt to connect to {};"
                                             " full error: {}".format(dependency, e))
                    service["status"] = "UNKNOWN"
                    overall_status = 500
                    service["status_code"] = None
                    service["content_type"] = None
                    service["content"] = None
                except Exception as e:  # Generic catch-all exception
                    current_app.logger.error("Unknown error occured during health cascade on request to {};"
                                             " full error: {}".format(dependency, e))
                    service["status"] = "UNKNOWN"
                    overall_status = 500
                    service["status_code"] = None
                    service["content_type"] = None
                    service["content"] = None
                else:   # Everything worked
                    service["status_code"] = resp.status_code
                    service["content_type"] = resp.headers["content-type"]
                    service["content"] = resp.json()
                    if resp.status_code == 200:  # Happy route, happy service, happy status_code.
                        service["status"] = "OK"
                    elif resp.status_code == 500:  # Something went wrong
                        service["status"] = "BAD"
                        overall_status = 500
                    else:   # Who knows what happened.
                        service["status"] = "UNKNOWN"
                        overall_status = 500
                finally:
                    services.append(service)
    response_json = {
        "cascade_depth": depth,
        "server_timestamp": str(datetime.datetime.now()),
        "app": current_app.config.get("APP_NAME"),
        "status": "UNKNOWN",
        "headers": request.headers.to_list(),
        "commit": current_app.config.get("COMMIT"),
        "db": dbs,
        "services": services
    }
    if overall_status == 500:
        response_json['status'] = "BAD"
    else:
        response_json['status'] = "OK"
    return Response(response=json.dumps(response_json), mimetype='application/json', status=overall_status)
