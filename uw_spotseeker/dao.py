# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Contains UW Spotseeker DAO implementations.
"""
from restclients_core.dao import DAO, LiveDAO
from restclients_core.models import MockHTTP
from django.http import HttpResponse
from os.path import abspath, dirname
from commonconf import settings
import os
import requests
from django.core.cache import cache

from logging import getLogger

logger = getLogger(__name__)


class Spotseeker_DAO(DAO):
    def service_name(self):
        return 'spotseeker'

    def service_mock_paths(self):
        path = [abspath(os.path.join(dirname(__file__), "resources"))]
        return path

    def _get_live_implementation(self):
        return Spotseeker_LiveDAO(self.service_name(), self)


class Spotseeker_LiveDAO(LiveDAO):
    # decrease cache expiry by epsilon seconds to account for time it takes to
    # get token and set in cache, and time it takes to make request once
    # retrieved from cache
    EPSILON = 60

    def load(self, method, url, headers, body) -> MockHTTP:
        if body is None:
            body = ''
        logger.debug(f'body: {body}')

        url = settings.RESTCLIENTS_SPOTSEEKER_HOST + url

        headers['Authorization'] = self.get_auth_header()

        if 'files' in headers:
            files = headers['files']
            del headers['files']
        else:
            files = None

        requests_response = requests.request(method,
                                             url,
                                             data=body,
                                             files=files,
                                             headers=headers)

        response = self.process_response(requests_response)

        return response

    def process_response(self, resp: HttpResponse) -> MockHTTP:
        response = MockHTTP()
        response.status = resp.status_code
        response.data = resp.content
        response.headers = resp.headers
        response.reason = resp.reason
        return response

    def set_token_in_cache(self, token: str, expiry: int) -> None:
        # set cache key to be app name
        key_name = settings.APP_NAME
        logger.debug(f'Setting {key_name} in cache for {expiry} seconds')
        cache.set(key_name, token, timeout=expiry - self.EPSILON)

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

        # console log token for debugging
        if token is None:
            logger.debug(f'No token found in cache for {key_name}')
            token = self.get_access_token()
        else:
            logger.debug(f'Using token from cache for {key_name}')

        return token

    def get_auth_header(self) -> str:
        token = self._get_access_token_from_cache()

        return f'Bearer {token}'
