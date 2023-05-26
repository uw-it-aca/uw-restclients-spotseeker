# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Contains UW Spotseeker DAO implementations.
"""
from restclients_core.dao import DAO, LiveDAO, MockDAO
from restclients_core.models import MockHTTP
from os.path import abspath, dirname
from commonconf import settings
import os
import requests
from django.core.cache import cache


class Spotseeker_DAO(MockDAO, DAO):

    def __init__(self):
        super().__init__(self.service_name(), self)
        self.log_start = None
        self.log_end = None
        self.log_timing = False

    def is_mock(self):
        return False

    def service_name(self):
        return 'spotseeker'

    def service_mock_paths(self):
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path

    def load(self, method, url, headers, body):
        # check headers for auth token
        unauth_response = MockHTTP()
        unauth_response.status = 403
        unauth_response.reason = 'Unauthorized'

        # check auth token
        auth_token = self.get_access_token()

        if settings.APP_NAME != self._get_token_app_name(auth_token):
            return unauth_response

        # if read not in scope, but method is GET, deny
        if settings.READ_SCOPE not in self._get_token_scope(auth_token) \
                and method.upper() == 'GET':
            return unauth_response

        # if write not in scope, but method is POST, PUT, or DELETE, deny
        if settings.WRITE_SCOPE not in self._get_token_scope(auth_token) \
                and method.upper() in ['POST', 'PUT', 'DELETE']:
            return unauth_response

        # path = self.service_mock_paths()

        return super().load(method, url, headers, body)

    def _get_live_implementation(self):
        return Spotseeker_LiveDAO(self.service_name(), self)
    
    def _get_mock_implementation(self):
        return self

    def _get_token_app_name(self, token: str) -> str:
        # get string between dummy_ and _token_, allows underscores in app name
        return token.split('_token_')[0].replace('dummy_', '')

    def _get_token_scope(self, token: str) -> str:
        # get string after _token_, allows underscores in scope
        return token.split('_token_')[1].replace('_', ' ')
    
    def get_access_token(self) -> str:
        scope = settings.SPOTSEEKER_OAUTH_SCOPE
        
        # ex: dummy_scout_token_read_write
        return f'dummy_{settings.APP_NAME}_token_{scope.replace(" ", "_")}'

    def get_auth_header(self) -> str:
        token = self.get_access_token()

        return f'Bearer {token}'


class Spotseeker_LiveDAO(LiveDAO):
    # decrease cache expiry by epsilon seconds to account for time it takes to
    # get token and set in cache, and time it takes to make request once
    # retrieved from cache
    EPSILON = 60

    def load(self, method, url, headers, body):
        if body is None:
            body = ''
        body = body.encode("utf-8")

        url = settings.RESTCLIENTS_SPOTSEEKER_HOST + url

        headers['Authorization'] = self.get_auth_header()
        resp = requests.request(method,
                                url,
                                data=body,
                                headers=headers)

        response = self.process_response(resp)
        return response

    def process_response(self, resp):
        response = MockHTTP()
        response.status = resp.status_code
        response.data = resp.content
        response.headers = resp.headers
        return response

    def set_token_in_cache(self, token: str, expiry: int) -> None:
        # set cache key to be app name
        key_name = settings.APP_NAME
        cache.set(key_name, token, timeout = expiry - self.EPSILON)

    def get_access_token(self) -> str:
        headers = {
            'Authorization': 'Basic ' + settings.SPOTSEEKER_OAUTH_CREDENTIAL,
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'client_credentials',
            'scope': settings.SPOTSEEKER_OAUTH_SCOPE,
        }

        url = settings.RESTCLIENTS_SPOTSEEKER_HOST + '/auth/token/'

        response = requests.post(url, headers=headers, data=data)

        json_resp = response.json()

        if 'access_token' not in json_resp:
            raise Exception(f'Error in authentication: {json_resp}')

        access_token = json_resp['access_token']
        expiry = json_resp['expires_in']
        self.set_token_in_cache(access_token, expiry)

        return access_token

    def _get_access_token_from_cache(self) -> str:
        # set cache key to be app name
        key_name = settings.APP_NAME
        token = cache.get(key_name)
        if token is None:
            token = self.get_access_token()

        return token

    def get_auth_header(self) -> str:
        token = self._get_access_token_from_cache()

        return f'Bearer {token}'
