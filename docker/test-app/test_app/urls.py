# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.urls import re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from .views import get_spots

urlpatterns = [
    # use functional view to return list of spots
    re_path(r"^$", get_spots, name="get_spots"),
]
