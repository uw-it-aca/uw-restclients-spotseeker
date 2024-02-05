# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
from .views import SpotView, SpotImageView, AllSpotsView, BuildingsView, \
     ItemImageView, NewSpotView, SpotEditView

urlpatterns = [
    path("spot/<int:spot_id>/image/<int:img_id>",
         csrf_exempt(SpotImageView.as_view())),
    path("spot/<int:spot_id>/image", csrf_exempt(SpotImageView.as_view())),

    path("item/<int:item_id>/image/<int:img_id>",
         csrf_exempt(ItemImageView.as_view())),
    path("item/<int:item_id>/image", csrf_exempt(ItemImageView.as_view())),

    path("spot/<int:spot_id>", csrf_exempt(SpotView.as_view()), name="spot"),
    path("spot", csrf_exempt(SpotView.as_view())),

    path("spot/<int:spot_id>/edit", csrf_exempt(SpotEditView.as_view())),

    path("spot/new", NewSpotView.as_view(), name="new_spot"),

    path("all", AllSpotsView.as_view()),

    path("buildings", BuildingsView.as_view(), name="get_buildings"),

    path("", RedirectView.as_view(url="all")),
]
