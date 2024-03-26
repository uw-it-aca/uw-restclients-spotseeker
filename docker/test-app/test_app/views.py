# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import HttpResponse
from django.views.generic.base import TemplateView, View
from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache
from uw_spotseeker import Spotseeker
import json
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


def get_token() -> str:
    cache_key = settings.APP_NAME + "-oauth"
    return cache.get(cache_key, 'no token in cache')


class BuildingsView(View):
    def get(self, request):
        spotseeker = Spotseeker()

        campus = request.GET.get('campus', 'seattle')
        app_type = request.GET.get('app_type')

        data = spotseeker.get_building_list(campus, app_type)
        return HttpResponse(json.dumps(data), content_type='application/json')


class AllSpotsView(TemplateView):
    template_name = 'all_spots.html'

    def get_context_data(self, **kwargs):
        context = super(AllSpotsView, self).get_context_data(**kwargs)
        spotseeker = Spotseeker()

        if kwargs.get('query'):
            spots = spotseeker.search_spots(kwargs.get('query'))
        else:
            spots = spotseeker.all_spots()

        context['spots'] = spots
        context['title'] = 'Spots'
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE
        context['token'] = get_token()

        return context

    def get(self, request):
        query = request.GET.dict()
        context = self.get_context_data(query=query)
        return render(request, self.template_name, context)


class SpotView(TemplateView):
    template_name = 'spot.html'

    def get_context_data(self, **kwargs):
        context = super(SpotView, self).get_context_data(**kwargs)
        spotseeker = Spotseeker()

        context['title'] = 'Spot'
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE
        context['token'] = get_token()
        context['spot'] = spotseeker.get_spot_by_id(kwargs.get('spot_id'))

        return context

    def get(self, request, spot_id):
        context = self.get_context_data(spot_id=spot_id)
        return render(request, self.template_name, context)

    def post(self, request):
        body = request.body
        spotseeker = Spotseeker()

        response = spotseeker.post_spot(body)
        return HttpResponse(response.data, status=response.status,
                            content_type=response.headers['Content-Type'])

    def delete(self, request, spot_id):
        spotseeker = Spotseeker()

        spot = spotseeker.get_spot_by_id(spot_id)
        etag = spot.etag
        _, _ = spotseeker.delete_spot(spot_id, etag)
        return HttpResponse(status=200)

    def put(self, request, spot_id):
        body = request.body
        spotseeker = Spotseeker()

        spot = spotseeker.get_spot_by_id(spot_id)
        etag = spot.etag
        response, _ = spotseeker.put_spot(spot_id, body, etag)
        return HttpResponse(response.data, status=response.status,
                            content_type=response.headers['Content-Type'])


class NewSpotView(TemplateView):
    template_name = 'new_spot.html'

    def get_context_data(self, **kwargs):
        context = super(NewSpotView, self).get_context_data(**kwargs)
        context['title'] = 'New Spot'
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE
        context['buildings'] = Spotseeker().get_building_list('seattle')
        context['token'] = get_token()

        return context

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)


class SpotEditView(TemplateView):
    template_name = 'spot_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        spotseeker = Spotseeker()

        context['title'] = 'Edit Spot'
        context['scope'] = settings.SPOTSEEKER_OAUTH_SCOPE
        context['buildings'] = spotseeker.get_building_list('seattle')
        context['token'] = get_token()
        context['spot'] = spotseeker.get_spot_by_id(kwargs.get('spot_id'))

        return context

    def get(self, request, spot_id):
        context = self.get_context_data(spot_id=spot_id)
        return render(request, self.template_name, context)


class SpotImageView(View):
    def get(self, request, spot_id, img_id):
        spotseeker = Spotseeker()
        resp, content = spotseeker.get_spot_image(spot_id, img_id)

        etag = resp.headers.get('etag')
        response = HttpResponse(content,
                                content_type=resp.headers['content-type'])
        response['etag'] = etag
        return response

    def post(self, request, spot_id):
        img = request.FILES.get('file')
        if not img:
            return HttpResponse(status=400)

        spotseeker = Spotseeker()
        image = spotseeker.post_image(spot_id, img)
        return HttpResponse(image)

    def delete(self, request, spot_id, img_id):
        spotseeker = Spotseeker()
        resp, _ = spotseeker.get_spot_image(spot_id, img_id)

        etag = resp.headers.get('etag')
        _ = spotseeker.delete_image(spot_id, img_id, etag)
        return HttpResponse(status=200)


class ItemImageView(View):
    def get(self, request, item_id, img_id):
        spotseeker = Spotseeker()
        resp, content = spotseeker.get_item_image(item_id, img_id)

        etag = resp.headers.get('etag')
        response = HttpResponse(content,
                                content_type=resp.headers['content-type'])
        response['etag'] = etag
        return response

    def post(self, request, item_id):
        img = request.FILES['file']
        if not img:
            return HttpResponse(status=400)

        spotseeker = Spotseeker()
        data = spotseeker.post_item_image(item_id, img)
        return HttpResponse(data)

    def delete(self, request, item_id, img_id):
        spotseeker = Spotseeker()
        resp, _ = spotseeker.get_item_image(item_id, img_id)

        etag = resp.headers.get('etag')
        spotseeker.delete_item_image(item_id, img_id, etag)
        return HttpResponse(status=200)
