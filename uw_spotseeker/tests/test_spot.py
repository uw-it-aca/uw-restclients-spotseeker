# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_spotseeker import Spotseeker
from uw_spotseeker.utilities import fdao_spotseeker_override
from restclients_core.exceptions import DataFailureException
from unittest import TestCase
from PIL import Image
import dateutil.parser
import os
import json
from io import BytesIO


@fdao_spotseeker_override
class SpotseekerTestSpot(TestCase):

    def test_get_all_spots(self):
        spotseeker = Spotseeker()
        all_spots = spotseeker.all_spots()
        self.assertEqual(len(all_spots), 3)

    def test_get_spot(self):
        spotseeker = Spotseeker()
        spot_data = spotseeker.get_spot_by_id(123)

        self.assertEqual(spot_data.spot_id, "123")
        self.assertEqual(spot_data.name, "Test Spot")
        self.assertEqual(spot_data.uri, "/api/v1/spot/123")
        self.assertEqual(spot_data.latitude, 3.60)
        self.assertEqual(spot_data.longitude, 1.34)
        self.assertEqual(spot_data.height_from_sea_level, 0.10)
        self.assertEqual(spot_data.building_name, "Test Building")
        self.assertEqual(spot_data.floor, 0)
        self.assertEqual(spot_data.room_number, "456")
        self.assertEqual(spot_data.capacity, 0)
        self.assertEqual(spot_data.display_access_restrictions, "none")
        self.assertEqual(spot_data.organization, "Test Org")
        self.assertEqual(spot_data.manager, "Mr Test Org")
        self.assertEqual(spot_data.etag, "686897696a7c876b7e")
        self.assertEqual(spot_data.external_id, "asd123")
        self.assertEqual(spot_data.last_modified,
                         dateutil.parser.parse("2012-07-13T05:00:00+00:00"))

        self._assert_spot_types(spot_data.spot_types, ["study_room", "cafe"])
        self.assertEqual(len(spot_data.images), 1)
        self.assertEqual(spot_data.images[0].image_id, "1")
        self.assertEqual(spot_data.images[0].url,
                         "/api/v1/spot/123/image/1")
        self.assertEqual(spot_data.images[0].content_type, "image/jpeg")
        self.assertEqual(spot_data.images[0].width, 0)
        self.assertEqual(spot_data.images[0].height, 0)
        self.assertEqual(spot_data.images[0].creation_date,
                         dateutil.parser.parse(
                         "Sun, 06 Nov 1994 08:49:37 GMT"))
        self.assertEqual(spot_data.images[0].modification_date,
                         dateutil.parser.parse(
                         "Mon, 07 Nov 1994 01:49:37 GMT"))
        self.assertEqual(spot_data.images[0].upload_user,
                         "user name")
        self.assertEqual(spot_data.images[0].upload_application,
                         "application name")
        self.assertEqual(spot_data.images[0].thumbnail_root,
                         "/api/v1/spot/123/image/1/thumb")
        self.assertEqual(spot_data.images[0].description,
                         "Information about the image")
        self.assertEqual(spot_data.images[0].display_index, 0)

        self.assertEqual(len(spot_data.spot_availability), 7)
        self._assert_spot_extended_info(spot_data.extended_info, [
            ("field2", 0),
            ("field3", 0.0),
            ("whiteboards", True)
        ])

    def test_search_spots(self):
        """ Tests search_spots function with mock data provided in the
            file named : spot?limit=5&center_latitude=47.653811&
                    center_longitude=-122.307815&distance=100000&
                    fuzzy_hours_start=Tuesday%2C05%3A00&fuzzy_hours_end=
                    Tuesday%2C11%3A00&extended_info%3Aapp_type=food
            tests mock data is accessible if filename matches order
            of query_tuple passed.
        """
        spotseeker = Spotseeker()
        query_tuple = [
                    ('limit', 5), ('center_latitude', u'47.653811'),
                    ('center_longitude', u'-122.307815'),
                    ('distance', 100000),
                    ('fuzzy_hours_start', 'Tuesday,05:00'),
                    ('fuzzy_hours_end', 'Tuesday,11:00'),
                    ('extended_info:app_type', 'food')]

        spot_data_list = spotseeker.search_spots(query_tuple)
        spot_data = spot_data_list[0]

        self.assertEqual(len(spot_data_list), 5)
        self.assertEqual(spot_data.spot_id, 40)
        self.assertEqual(spot_data.name, "TestSpot1")
        self.assertEqual(spot_data.uri, "/api/v1/spot/40")
        self.assertEqual(spot_data.latitude, 47)
        self.assertEqual(spot_data.longitude, -12)
        self.assertEqual(spot_data.height_from_sea_level, 0.10)
        self.assertEqual(spot_data.building_name, "TestBuilding")
        self.assertEqual(spot_data.capacity, 0)
        self.assertEqual(spot_data.organization, "Test Org")
        self.assertEqual(spot_data.manager, "Test Manager")
        self.assertEqual(spot_data.etag, "123456789")
        self.assertEqual(spot_data.last_modified,
                         dateutil.parser.parse("2012-07-13T05:00:00+00:00"))

        self.assertEqual(len(spot_data.images), 1)
        self.assertEqual(spot_data.images[0].image_id, "1")
        self.assertEqual(spot_data.images[0].url,
                         "/api/v1/spot/123/image/1")
        self.assertEqual(spot_data.images[0].content_type, "image/jpeg")
        self.assertEqual(spot_data.images[0].width, 0)
        self.assertEqual(spot_data.images[0].height, 0)
        self.assertEqual(spot_data.images[0].creation_date,
                         dateutil.parser.parse(
                         "Sun, 06 Nov 1994 08:49:37 GMT"))
        self.assertEqual(spot_data.images[0].modification_date,
                         dateutil.parser.parse(
                         "Mon, 07 Nov 1994 01:49:37 GMT"))
        self.assertEqual(spot_data.images[0].upload_user,
                         "user name")
        self.assertEqual(spot_data.images[0].upload_application,
                         "application name")
        self.assertEqual(spot_data.images[0].thumbnail_root,
                         "/api/v1/spot/123/image/1/thumb")
        self.assertEqual(spot_data.images[0].description,
                         "Information about the image")
        self.assertEqual(spot_data.images[0].display_index, 0)

        self.assertEqual(len(spot_data.spot_availability), 5)

    def test_spot_items(self):
        spotseeker = Spotseeker()
        spot_data = spotseeker.get_spot_by_id(1)
        self.assertEqual(len(spot_data.items), 2)

    def test_bad_spot(self):
        spotseeker = Spotseeker()
        self.assertRaises(DataFailureException,
                          spotseeker.get_spot_by_id, 999)

    def test_post_spot(self):
        spotseeker = Spotseeker()
        spot_data = spotseeker.get_spot_by_id(1)
        self.assertRaises(DataFailureException,
                          spotseeker.post_spot, spot_data)

    def test_delete_spot(self):
        spotseeker = Spotseeker()
        spot_data = spotseeker.get_spot_by_id(1)
        response, content = spotseeker.delete_spot(1, "XXX")
        result = json.loads(content.decode('utf-8'))
        self.assertEqual(spot_data.spot_id, result["id"])

    def test_put_spot(self):
        spotseeker = Spotseeker()
        directory = os.path.dirname(__file__)
        path = "../resources/spotseeker/file/api/v1/spot/1"
        mock_path = os.path.join(directory, path)
        with open(mock_path) as f:
            spot_json = json.load(f)
        response, content = spotseeker.put_spot(1, spot_json, "XXX")
        self.assertEqual(json.loads(content.decode('utf-8')), spot_json)

    def test_building_list(self):
        spotseeker = Spotseeker()
        buildings = spotseeker.get_building_list("seattle")
        self.assertEqual(len(buildings), 43)

    def test_get_image(self):
        directory = os.path.dirname(__file__)
        path = "../resources/spotseeker/file/api/v1/spot/20/image/1"
        mock_path = os.path.join(directory, path)
        with open(mock_path, "rb") as f:
            expected_img = Image.open(BytesIO(bytearray(f.read())))

        spotseeker = Spotseeker()
        response, content = spotseeker.get_spot_image(20, 1)
        byte_img = bytearray(response.data)
        img = Image.open(BytesIO(byte_img))
        self.assertEqual(img, expected_img)

    def test_post_image(self):
        spotseeker = Spotseeker()
        response = spotseeker.post_image(6, b'')
        self.assertEqual(response, b'')

    def test_delete_image(self):
        spotseeker = Spotseeker()
        response = spotseeker.delete_image(20, 1, "XXX")

    def test_post_item_image(self):
        spotseeker = Spotseeker()
        response = spotseeker.post_item_image(1, b'')
        self.assertEqual(response, b'')

    def test_delete_item_image(self):
        spotseeker = Spotseeker()
        response = spotseeker.delete_item_image(20, 1, "XXX")

    def _assert_spot_types(self, spot_types, type_stings):
        spot_types = [spot_type.name for spot_type in spot_types]
        self.assertEqual(set(spot_types), set(type_stings))

    def _assert_spot_extended_info(self, spot_ei_data, ei_tuples):
        spot_ei_tuples = [(spot_ei.key, spot_ei.value)
                          for spot_ei
                          in spot_ei_data]
        self.assertEqual(set(spot_ei_tuples), set(ei_tuples))
