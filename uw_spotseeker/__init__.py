"""
This is the interface for interacting with the Spotseeker Server REST API
"""

from restclients_core.exceptions import DataFailureException
from uw_spotseeker.dao import Spotseeker_DAO
from uw_spotseeker.models import (
    Spot, SpotType, SpotAvailableHours, SpotExtendedInfo)
from uw_spotseeker.exceptions import InvalidSpotID
import json
import dateutil.parser
import re
import six
import datetime


class Spotseeker(object):

    def all_spots(self):
        url = "/api/v1/spot/all"
        response = Spotseeker_DAO().getURL(url)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)

        results = json.loads(response.data)

        spots = self._spots_from_data(results)
        return spots

    def get_spot_by_id(self, spot_id):
        self._validate_spotid(spot_id)

        url = "/api/v1/spot/%s" % spot_id
        response = Spotseeker_DAO().getURL(url)

        if response.status != 200:
            raise DataFailureException(url, response.status, response.data)
        return self._spot_from_data(json.loads(response.data))

    def _spots_from_data(self, spots_data):
        return [self._spot_from_data(spot_data) for spot_data in spots_data]

    def _spot_from_data(self, spot_data):
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
        # spot.images = self._spot_images_from_data(spot_data["images"])
        spot.extended_info = \
            self._extended_info_from_data(spot_data["extended_info"])
        # spot.items = []
        # if "items" in spot_data and len(spot_data["items"]) > 0:
        #     spot.items = self._items_from_data(spot_data["items"])

        return spot

    # def _items_from_data(self, item_data):
    #     spot_items = []
    #     for item in item_data:
    #         spot_item = SpotItem()
    #         spot_item.item_id = item["id"]
    #         spot_item.name = item["name"]
    #         spot_item.category = item["category"]
    #         spot_item.subcategory = item["subcategory"]
    #         spot_item.images = []
    #         if "images" in item and len(item["images"]) > 0:
    #            spot_item.images = self._item_images_from_data(item["images"])
    #         spot_item.extended_info = \
    #             self._extended_info_from_data(item["extended_info"])
    #         spot_items.append(spot_item)
    #     return spot_items

    def _spot_availability_from_data(self, avaliblity_data):
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
            kw = {k: int(v) for k, v in six.iteritems(kw) if v is not None}
            return datetime.time(**kw)

    def _spot_types_from_data(self, type_data):
        spot_types = []
        for spot_type in type_data:
            spot_types.append(SpotType(name=spot_type))
        return spot_types

    def _validate_spotid(self, spotid):
        if (not type(spotid) is int):
            raise InvalidSpotID

    def _extended_info_from_data(self, info_data):
        extended_info = []

        for attribute in info_data:
            spot_extended_info = SpotExtendedInfo(key=attribute,
                                                  value=info_data[attribute])
            extended_info.append(spot_extended_info)
        return extended_info
