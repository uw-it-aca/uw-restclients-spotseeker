# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import HttpResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from uw_spotseeker import Spotseeker
import json
import logging

logging.basicConfig()
logger = logging.getLogger("test_app")

# functional view to return list of spots
def get_spots(request):
    spotseeker = Spotseeker()
    spots = spotseeker.all_spots()
    return HttpResponse(spots)
