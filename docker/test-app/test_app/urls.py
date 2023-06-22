# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import SearchSpotsView, SpotView, ItemImageView, SpotImageView, \
     AllSpotsView, BuildingsView

urlpatterns = [
    path("spot/<int:spot_id>/image/<int:img_id>",
         csrf_exempt(SpotImageView.as_view())),
    path("spot/<int:spot_id>/image", csrf_exempt(SpotImageView.as_view())),

    path("item/<int:item_id>/image/<int:img_id>",
         csrf_exempt(ItemImageView.as_view())),
    path("item/<int:item_id>/image", csrf_exempt(ItemImageView.as_view())),

    path("spot/<int:spot_id>", csrf_exempt(SpotView.as_view())),
    path("spot", csrf_exempt(SpotView.as_view())),

    path("all", AllSpotsView.as_view()),

    path("buildings", BuildingsView.as_view(), name="get_buildings"),

    path("search", SearchSpotsView.as_view(), name="get_spots_by_search"),
]
