"""
Contains UW Spotseeker DAO implementations.
"""
from restclients_core.dao import DAO, LiveDAO
from os.path import abspath, dirname
from django.conf import settings
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
        consumer = oauth2.Consumer(key=settings.SPOTSEEKER_OAUTH_KEY,
                                   secret=settings.SPOTSEEKER_OAUTH_SECRET)
        client = oauth2.Client(consumer)
        url = settings.RESTCLIENTS_SPOTSEEKER_HOST + url

        resp, content = client.request(url,
                                       method=method,
                                       body=body,
                                       headers=headers)
        return resp
