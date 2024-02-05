# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This is the interface for interacting with the Spotseeker Server REST API
"""

from restclients_core.exceptions import DataFailureException
from restclients_core.models import MockHTTP
from uw_spotseeker.dao import Spotseeker_DAO
from uw_spotseeker.models import (Spot, SpotType, SpotImage, ItemImage,
                                  SpotItem, SpotAvailableHours,
                                  SpotExtendedInfo)
from uw_spotseeker.exceptions import InvalidSpotID
from typing import Tuple, List
import json
import dateutil.parser
import re
import datetime
import logging
import os
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class Spotseeker(object):

    def _post_image(self, url, image: bytes) -> bytes:
        headers = {"X-OAuth-User": os.getenv('OAUTH_USER')}
        headers['files'] = {'image': ('image.jpg', image)}

        response = Spotseeker_DAO().postURL(url, headers)
        content = response.data
        status = response.status
        if status not in (200, 201):
            raise DataFailureException(url, status,
                                       getattr(response, 'reason', content))

        return content

    def _delete_image(self, url, etag) -> None:
        headers = {"X-OAuth-User": os.getenv('OAUTH_USER'),
                   "If-Match": etag}
        response = Spotseeker_DAO().deleteURL(url, headers)
        content = response.data
        status = response.status

        if status != 200:
            raise DataFailureException(url, status,
                                       getattr(response, 'reason', content))

    def post_image(self, spot_id, image: bytes) -> bytes:
        url = "/api/v1/spot/%s/image" % spot_id
        return self._post_image(url, image)

    def post_item_image(self, item_id, image: bytes) -> bytes:
        url = "/api/v1/item/%s/image" % item_id
        return self._post_image(url, image)

    def delete_image(self, spot_id, image_id, etag) -> None:
        url = "/api/v1/spot/%s/image/%s" % (spot_id, image_id)
        self._delete_image(url, etag)
        return None

    def delete_item_image(self, item_id, image_id, etag) -> None:
        url = "/api/v1/item/%s/image/%s" % (item_id, image_id)
        self._delete_image(url, etag)
        return None

    def _get_spots_json(self, url):
        response = Spotseeker_DAO().getURL(url)
        status = response.status
        content = response.data

        if status != 200:
            raise DataFailureException(url, status, content)

        results = json.loads(content.decode('utf-8'))
        return results

    def get_filtered_spots_json(self, filters=[]) -> List[dict]:
        """
        Returns a list of spots matching the passed parameters
        """

        url = "/api/v1/spot?" + urlencode(filters)
        return self._get_spots_json(url)

    def get_spot_by_id_json(self, spot_id: int) -> dict:
        """
        Returns a list of spots matching the passed parameters
        """

        self._validate_spotid(spot_id)
        url = "/api/v1/spot/%s" % spot_id
        return self._get_spots_json(url)

    def get_all_spots_json(self) -> List[dict]:
        """
        Returns a list of all spots
        """

        url = "/api/v1/spot/all"
        return self._get_spots_json(url)

    def all_spots(self) -> List[Spot]:
        url = "/api/v1/spot/all"
        results = self._get_spots_json(url)
        return self._spots_from_data(results)

    def search_spots(self, query_tuple) -> List[Spot]:
        """
        Returns a list of spots matching the passed parameters
        """

        url = "/api/v1/spot?" + urlencode(query_tuple)
        results = self._get_spots_json(url)
        return self._spots_from_data(results)

    def put_spot(self, spot_id, spot_json: str, etag) -> Tuple[MockHTTP,
                                                               bytes]:
        url = "/api/v1/spot/%s" % spot_id
        headers = {"X-OAuth-User": os.getenv('OAUTH_USER'),
                   "If-Match": etag}
        response = Spotseeker_DAO().putURL(url, headers, spot_json)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        return response, response.data

    def delete_spot(self, spot_id, etag) -> Tuple[MockHTTP, bytes]:
        url = "/api/v1/spot/%s" % spot_id
        headers = {"X-OAuth-User": os.getenv('OAUTH_USER'),
                   "If-Match": etag}
        response = Spotseeker_DAO().deleteURL(url, headers)

        content = response.data
        status = response.status

        if status != 200:
            raise DataFailureException(url, status, content)

        return response, content

    def post_spot(self, spot_json: str) -> MockHTTP:
        url = "/api/v1/spot"
        headers = {"X-OAuth-User": os.getenv('OAUTH_USER'),
                   "Content-Type": "application/json"}
        response = Spotseeker_DAO().postURL(url, headers, spot_json)

        content = response.data
        status = response.status

        if status != 201:
            raise DataFailureException(url, status, content)

        return response

    def get_spot_by_id(self, spot_id: int) -> Spot:
        self._validate_spotid(spot_id)
        url = "/api/v1/spot/%s" % spot_id
        results = self._get_spots_json(url)
        return self._spot_from_data(results)

    def get_building_list(self, campus, app_type=None) -> List[dict]:
        url = "/api/v1/buildings?extended_info:campus=" + campus
        if app_type:
            url += "&extended_info:app_type=" + app_type

        return self._get_spots_json(url)

    def get_spots_from_json(self, json_data) -> List[Spot]:
        return self._spots_from_data(json_data)

    def _spots_from_data(self, spots_data) -> List[Spot]:
        return [self._spot_from_data(spot_data) for spot_data in spots_data]

    def _spot_from_data(self, spot_data) -> Spot:
        spot = Spot()

        spot.spot_id = spot_data["id"]
        spot.name = spot_data["name"]
        spot.uri = spot_data["uri"]
        spot.latitude = spot_data["location"]["latitude"]
        spot.longitude = spot_data["location"]["longitude"]
        spot.height_from_sea_level = \
            spot_data["location"]["height_from_sea_level"]
        spot.building_name = spot_data["location"]["building_name"]
        spot.building_description = spot_data["location"].get("description",
                                                              None)
        spot.floor = spot_data["location"]["floor"]
        spot.room_number = spot_data["location"]["room_number"]
        spot.capacity = spot_data["capacity"]
        spot.display_access_restrictions = \
            spot_data["display_access_restrictions"]
        spot.organization = spot_data["organization"]
        spot.manager = spot_data["manager"]
        spot.etag = spot_data["etag"]
        spot.external_id = spot_data["external_id"]

        spot.last_modified = dateutil.parser.parse(spot_data["last_modified"])
        spot.spot_types = self._spot_types_from_data(spot_data["type"])
        spot.spot_availability = \
            self._spot_availability_from_data(spot_data["available_hours"])
        spot.images = self._spot_images_from_data(spot_data["images"])
        spot.extended_info = \
            self._extended_info_from_data(spot_data["extended_info"])
        spot.items = []
        if "items" in spot_data and len(spot_data["items"]) > 0:
            spot.items = self._items_from_data(spot_data["items"])

        return spot

    def _items_from_data(self, item_data) -> List[SpotItem]:
        spot_items = []
        for item in item_data:
            spot_item = SpotItem()
            spot_item.item_id = item["id"]
            spot_item.name = item["name"]
            spot_item.category = item["category"]
            spot_item.subcategory = item["subcategory"]
            spot_item.images = []
            if "images" in item and len(item["images"]) > 0:
                spot_item.images = self._item_images_from_data(item["images"])
            spot_item.extended_info = \
                self._extended_info_from_data(item["extended_info"])
            spot_items.append(spot_item)
        return spot_items

    def _item_images_from_data(self, image_data) -> List[ItemImage]:
        images = []

        for image in image_data:
            item_image = ItemImage()
            item_image.image_id = image["id"]
            item_image.url = image["url"]
            item_image.description = image["description"]
            item_image.display_index = image["display_index"]
            item_image.content_type = image["content-type"]
            item_image.width = image["width"]
            item_image.height = image["height"]
            item_image.creation_date = dateutil.parser.parse(
                                       image["creation_date"])
            item_image.upload_user = image["upload_user"]
            item_image.upload_application = image["upload_application"]
            item_image.thumbnail_root = image["thumbnail_root"]

            images.append(item_image)

        return images

    def _spot_images_from_data(self, image_data) -> List[SpotImage]:
        images = []

        for image in image_data:
            spot_image = SpotImage()
            spot_image.image_id = image["id"]
            spot_image.url = image["url"]
            spot_image.description = image["description"]
            spot_image.display_index = image["display_index"]
            spot_image.content_type = image["content-type"]
            spot_image.width = image["width"]
            spot_image.height = image["height"]
            spot_image.creation_date = dateutil.parser.parse(
                                       image["creation_date"])
            spot_image.modification_date = \
                dateutil.parser.parse(image["modification_date"])
            spot_image.upload_user = image["upload_user"]
            spot_image.upload_application = image["upload_application"]
            spot_image.thumbnail_root = image["thumbnail_root"]

            images.append(spot_image)

        return images

    def _spot_availability_from_data(
            self, avaliblity_data) -> List[SpotAvailableHours]:
        availability = []

        for day in avaliblity_data:
            for hours in avaliblity_data[day]:
                available_hours = SpotAvailableHours()
                available_hours.day = day
                available_hours.start_time = self._parse_time(hours[0])
                available_hours.end_time = self._parse_time(hours[1])
                availability.append(available_hours)
        return availability

    def _parse_time(self, value):
        time_re = re.compile(
            r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
            r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
        )
        match = time_re.match(value)
        if match:
            kw = match.groupdict()
            if kw['microsecond']:
                kw['microsecond'] = kw['microsecond'].ljust(6, '0')
            kw = {k: int(v) for k, v in kw.items() if v is not None}
            return datetime.time(**kw)

    def _spot_types_from_data(self, type_data) -> List[SpotType]:
        spot_types = []
        for spot_type in type_data:
            spot_types.append(SpotType(name=spot_type))
        return spot_types

    def _validate_spotid(self, spotid):
        if (not type(spotid) is int):
            raise InvalidSpotID

    def _extended_info_from_data(self, info_data) -> List[SpotExtendedInfo]:
        extended_info = []

        for attribute in info_data:
            spot_extended_info = SpotExtendedInfo(key=attribute,
                                                  value=info_data[attribute])
            extended_info.append(spot_extended_info)
        return extended_info

    def _get_image(self, image_app_type, parent_id,
                   image_id, width=None) -> Tuple[MockHTTP, bytes]:
        if width is not None:
            url = "/api/v1/%s/%s/image/%s/thumb/constrain/width:%s" % (
                image_app_type,
                parent_id,
                image_id,
                width)
        else:
            url = "/api/v1/%s/%s/image/%s" % (image_app_type,
                                              parent_id,
                                              image_id)

        response = Spotseeker_DAO().getURL(url)
        content = response.data

        return response, content

    def get_item_image(self, parent_id,
                       image_id, width=None) -> Tuple[MockHTTP, bytes]:
        return self._get_image("item", parent_id, image_id, width)

    def get_spot_image(self, parent_id,
                       image_id, width=None) -> Tuple[MockHTTP, bytes]:
        return self._get_image("spot", parent_id, image_id, width)
