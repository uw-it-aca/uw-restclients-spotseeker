# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import HttpResponse
from django.views.generic.base import View, TemplateView
from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
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


class BuildingsView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super(BuildingsView, self).get_context_data(**kwargs)
        spotseeker = Spotseeker()
        buildings = spotseeker.get_building_list(kwargs.get('campus'),
                                                 kwargs.get('app_type'))
        context['data'] = buildings
        context['title'] = "All Buildings"
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE

        token = cache.get(settings.APP_NAME)
        if token is None:
            context['token'] = 'no token in cache'
        else:
            context['token'] = token
        return context

    def get(self, request, *args, **kwargs):
        campus = request.GET.get('campus', 'seattle')
        app_type = request.GET.get('app_type')
        context = self.get_context_data(**kwargs, campus=campus,
                                        app_type=app_type)
        return render(request, self.template_name, context)


class AllSpotsView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super(AllSpotsView, self).get_context_data(**kwargs)
        spotseeker = Spotseeker()
        spots = spotseeker.all_spots()
        context['data'] = [str(spot) for spot in spots]
        context['title'] = "All Spots"
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE
        token = cache.get(settings.APP_NAME)

        if token is None:
            context['token'] = 'no token in cache'
        else:
            context['token'] = token
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class SearchSpotsView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super(SearchSpotsView, self).get_context_data(**kwargs)
        spotseeker = Spotseeker()
        spots = spotseeker.search_spots(kwargs.get('query'))
        context['data'] = [str(spot) for spot in spots]
        context['title'] = "Search Spots"
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE

        token = cache.get(settings.APP_NAME)
        if token is None:
            context['token'] = 'no token in cache'
        else:
            context['token'] = token
        return context

    def get(self, request, *args, **kwargs):
        query = request.GET.dict()
        context = self.get_context_data(**kwargs, query=query)
        return render(request, self.template_name, context)


class SpotView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        context = super(SpotView, self).get_context_data(**kwargs)
        spot = kwargs.get('spot')
        context['data'] = str(spot)
        context['title'] = "Spot"
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE

        token = cache.get(settings.APP_NAME, None)
        if token is None:
            context['token'] = 'no token in cache'
        else:
            context['token'] = token
        return context

    def get(self, request, spot_id):
        spotseeker = Spotseeker()
        spots = spotseeker.get_spot_by_id(spot_id)
        return render(request, self.template_name,
                      self.get_context_data(spot=spots))

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
