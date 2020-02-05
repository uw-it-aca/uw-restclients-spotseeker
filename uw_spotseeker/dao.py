"""
Contains UW Spotseeker DAO implementations.
"""
from restclients_core.dao import DAO, LiveDAO
from restclients_core.models import MockHTTP
from os.path import abspath, dirname
from commonconf import settings
import base64
import os
import oauth2


class Spotseeker_DAO(DAO):
    def service_name(self):
        return 'spotseeker'

    def service_mock_paths(self):
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path

    def _get_live_implementation(self):
        return Spotseeker_LiveDAO(self.service_name(), self)


class Spotseeker_LiveDAO(LiveDAO):
    def load(self, method, url, headers, body):
        if body is None:
            body = bytes('', 'utf-8')
        else:
            body = base64.b64encode(body.encode())

        consumer = oauth2.Consumer(key=settings.SPOTSEEKER_OAUTH_KEY,
                                   secret=settings.SPOTSEEKER_OAUTH_SECRET)
        client = oauth2.Client(consumer)
        url = settings.RESTCLIENTS_SPOTSEEKER_HOST + url

        resp, content = client.request(url,
                                       method=method,
                                       body=body,
                                       headers=headers)
        response = self.process_response(resp, content)
        return response

    def process_response(self, headers, data):
        response = MockHTTP()
        response.status = int(headers['status'])
        response.data = data
        response.headers = headers
        return response
