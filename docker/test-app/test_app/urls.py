# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import get_spots, get_buildings, get_spots_by_search, \
     SpotView, ItemImageView, SpotImageView

urlpatterns = [
    path("spot/<int:spot_id>/image/<int:img_id>",
         csrf_exempt(SpotImageView.as_view())),
    path("spot/<int:spot_id>/image", csrf_exempt(SpotImageView.as_view())),

    path("item/<int:item_id>/image/<int:img_id>",
         csrf_exempt(ItemImageView.as_view())),
    path("item/<int:item_id>/image", csrf_exempt(ItemImageView.as_view())),

    path("spot/<int:spot_id>", csrf_exempt(SpotView.as_view())),
    path("spot", csrf_exempt(SpotView.as_view())),

    path("all", get_spots),

    path("buildings", get_buildings, name="get_buildings"),

    path("search", get_spots_by_search, name="get_spots_by_search"),
]
