# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from .base_settings import *

if os.getenv("ENV", "localdev") == "localdev":
    DEBUG = True
else:
    DEBUG = False

APP_NAME = os.getenv("APP_NAME", "test-app")

# spotseeker server api stuff
RESTCLIENTS_SPOTSEEKER_HOST = os.getenv("RESTCLIENTS_SPOTSEEKER_HOST", None)
RESTCLIENTS_SPOTSEEKER_DAO_CLASS = os.getenv(
    "RESTCLIENTS_SPOTSEEKER_DAO_CLASS", "Mock"
)
SPOTSEEKER_OAUTH_CREDENTIAL = os.getenv("CREDENTIAL", "")

READ_SCOPE = os.getenv("READ_SCOPE", "read")
WRITE_SCOPE = os.getenv("WRITE_SCOPE", "write")
SPOTSEEKER_OAUTH_SCOPE = os.getenv("SCOPE", READ_SCOPE)

OAUTH_USER = os.getenv("OAUTH_USER", "")

if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-app',
        }
    }
