# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from uw_spotseeker import Spotseeker
import json
import logging
import requests

logging.basicConfig()
logger = logging.getLogger(__name__)


example_spot = json.dumps({
    'spot_id': 200,
    'name': 'Example Spot',
    'latitude': 47.6538,
    'longitude': -122.3078,
    'capacity': 10,
    'building_name': 'Guggenheim Hall',
    'building_description': 'Guggenheim Hall is a building.',
    'etag': '1234567890',
    'manager': 'javerage',
    'uri': '/api/v1/spot/200',
    'last_modified': '2012-07-13T05:00:00+00:00',
    'extended_info': {
        'has_whiteboards': 'true',
    }
})


response = requests.get('https://picsum.photos/id/237/200/300')
example_img = response.content


# functional view to return list of spots


@csrf_exempt
def get_buildings(request) -> HttpResponse:
    campus = request.GET.get('campus', 'seattle')
    app_type = request.GET.get('app_type')

    spotseeker = Spotseeker()
    buildings = spotseeker.get_building_list(campus, app_type)
    return HttpResponse(buildings)


@csrf_exempt
def get_spots(request) -> HttpResponse:
    spotseeker = Spotseeker()
    spots = spotseeker.all_spots()
    return HttpResponse(spots)


@csrf_exempt
def get_spots_by_search(request) -> HttpResponse:
    query = request.GET.dict()

    spotseeker = Spotseeker()
    spots = spotseeker.search_spots(query)
    return HttpResponse(spots)


class SpotView(View):
    def get(self, request, spot_id):
        spotseeker = Spotseeker()
        spots = spotseeker.get_spot_by_id(spot_id)
        return HttpResponse(spots)

    def post(self, request):
        body = request.body
        if not body:
            body = example_spot

        spotseeker = Spotseeker()
        response = spotseeker.post_spot(body)
        return HttpResponse(response.data, status=response.status,
                            content_type=response.headers['Content-Type'])

    def delete(self, request, spot_id):
        spotseeker = Spotseeker()
        spot = spotseeker.get_spot_by_id(spot_id)
        etag = spot.etag
        response = spotseeker.delete_spot(spot_id, etag)
        return HttpResponse(status=200)

    def put(self, request, spot_id):
        body = request.body
        if not body:
            body = example_spot

        spotseeker = Spotseeker()
        spot = spotseeker.get_spot_by_id(spot_id)
        etag = spot.etag
        response, _ = spotseeker.put_spot(spot_id, body, etag)
        return HttpResponse(response.data, status=response.status,
                            content_type=response.headers['Content-Type'])


class SpotImageView(View):
    def get(self, request, spot_id, img_id):
        spotseeker = Spotseeker()
        resp, content = spotseeker.get_spot_image(spot_id, img_id)

        etag = resp.headers.get('etag', None)
        response = HttpResponse(content,
                                content_type=resp.headers['content-type'])
        response['etag'] = etag
        return response

    def post(self, request, spot_id):
        img = request.FILES.get('file', None)
        if not img:
            img = example_img

        spotseeker = Spotseeker()
        image = spotseeker.post_image(spot_id, img)
        return HttpResponse(image)

    def delete(self, request, spot_id, img_id):
        spotseeker = Spotseeker()
        resp, _ = spotseeker.get_spot_image(spot_id, img_id)

        etag = resp.headers.get('etag', None)
        response = spotseeker.delete_image(spot_id, img_id, etag)
        return HttpResponse(status=200)


class ItemImageView(View):
    def get(self, request, item_id, img_id):
        spotseeker = Spotseeker()
        resp, content = spotseeker.get_item_image(item_id, img_id)

        etag = resp.headers.get('etag', None)
        response = HttpResponse(content,
                                content_type=resp.headers['content-type'])
        response['etag'] = etag
        return response

    def post(self, request, item_id):
        img = request.FILES['file']
        if not img:
            img = example_img

        spotseeker = Spotseeker()
        data = spotseeker.post_item_image(item_id, img)
        return HttpResponse(data)

    def delete(self, request, item_id, img_id):
        spotseeker = Spotseeker()

        resp, _ = spotseeker.get_item_image(item_id, img_id)
        etag = resp.etag

        spotseeker.delete_item_image(item_id, img_id, etag)
        return HttpResponse(status=200)
