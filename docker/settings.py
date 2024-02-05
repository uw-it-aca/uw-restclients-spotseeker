# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from .base_settings import *

if os.getenv("ENV", "localdev") == "localdev":
    DEBUG = True
else:
    DEBUG = False

APP_NAME = os.getenv("APP_NAME", "test-app")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'test_app', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

# spotseeker server api stuff
RESTCLIENTS_SPOTSEEKER_HOST = os.getenv("RESTCLIENTS_SPOTSEEKER_HOST", None)
RESTCLIENTS_SPOTSEEKER_DAO_CLASS = os.getenv(
    "RESTCLIENTS_SPOTSEEKER_DAO_CLASS", "Mock"
)
SPOTSEEKER_OAUTH_CREDENTIAL = os.getenv("CREDENTIAL", "")

READ_SCOPE = os.getenv("READ_SCOPE", "read")
WRITE_SCOPE = os.getenv("WRITE_SCOPE", "write")
SPOTSEEKER_OAUTH_SCOPE = os.getenv("SPOTSEEKER_OAUTH_SCOPE", READ_SCOPE)

OAUTH_USER = os.getenv("OAUTH_USER", "")

DEBUG_CACHING = os.getenv("DEBUG_CACHING", "True") == "True"

if DEBUG and not DEBUG_CACHING:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': APP_NAME,
        }
    }
