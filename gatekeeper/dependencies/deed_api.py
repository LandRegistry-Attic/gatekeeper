from flask import current_app, g
from gatekeeper.app import app
import json


class DeedApi(object):
    """Encapsulating class for Deed API access."""
    def __init__(self):
        super(DeedApi, self).__init__()
        self.deed_api_url = current_app.config["DEED_API_URL"]

    def health(self):
        app.logger.info('Calling get health')
        resp = self._process_request('', 'health', 'GET')

        return resp

    def get_deed(self, deed_reference, headers):
        app.logger.info('Calling get deed')
        resp = self._process_request('/' + str(deed_reference), 'deed', 'GET', headers)

        return resp

    def get_metrics(self, status, headers):
        app.logger.info('Calling get metrics')
        resp = self._process_request('/' + str(status), 'dashboard', 'GET', headers)

        return resp

    def create_deed(self, payload, headers):
        app.logger.info('Calling create deed')
        resp = self._process_request('/', 'deed', 'POST', headers, payload)

        return resp

    def make_effective(self, deed_reference, headers):
        app.logger.info('Calling make effective')
        resp = self._process_request('/' + str(deed_reference) + '/make-effective', 'deed', 'POST', headers)

        return resp

    def retrieve_signed(self, headers):
        app.logger.info('Calling retrieve signed')
        resp = self._process_request('/retrieve-signed', 'deed', 'GET', headers)

        return resp

    def _process_request(self, path, blueprint, method, headers=None, payload=None):
        url = '{0}/{1}{2}'

        if method == "POST":
            app.logger.info('making POST request to deed API')
            resp = g.requests.post(url.format(self.deed_api_url, blueprint, path), headers=headers, data=json.dumps(payload))
        else:
            app.logger.info('making GET request to deed API')

            new_headers = {}
            if headers is not None:
                for header in headers:
                    if header[0] != 'Content-Length':
                        new_headers[header[0]] = header[1]

            resp = g.requests.get(url.format(self.deed_api_url, blueprint, path), headers=new_headers)

        return resp
