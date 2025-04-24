import logging
from collections import namedtuple

import requests
import json
from math import radians, sqrt, sin, cos, atan2

from notfellchen import __version__ as nf_version
from notfellchen import settings

Position = namedtuple('Position', ['latitude', 'longitude'])


def zoom_level_for_radius(radius) -> int:
    if radius is None:
        return 4
    if radius <= 20:
        return 8
    if radius <= 50:
        return 7
    if radius <= 150:
        return 6
    if radius <= 300:
        return 5
    else:
        return 4


def calculate_distance_between_coordinates(position1, position2):
    """
    Calculate the distance between two points identified by coordinates
    It expects the coordinates to be a tuple (lat, lon)

    Based on https://en.wikipedia.org/wiki/Haversine_formula
    """
    earth_radius_km = 6371
    latitude1 = float(position1[0])
    longitude1 = float(position1[1])
    latitude2 = float(position2[0])
    longitude2 = float(position2[1])

    distance_lat = radians(latitude2 - latitude1)
    distance_long = radians(longitude2 - longitude1)

    a = pow(sin(distance_lat / 2), 2) + cos(radians(latitude1)) * cos(radians(latitude2)) * pow(sin(distance_long / 2),
                                                                                                2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_in_km = earth_radius_km * c

    logging.debug(f"Calculated Distance: {distance_in_km:.5}km")

    return distance_in_km


class ResponseMock:
    content = b'[{"place_id":138181499,"licence":"Data \xc2\xa9 OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright","osm_type":"relation","osm_id":1247237,"lat":"48.4949904","lon":"9.040330235970146","category":"boundary","type":"postal_code","place_rank":21, "importance":0.12006895017929346,"addresstype":"postcode","name":"72072","display_name":"72072, Derendingen, T\xc3\xbcbingen, Landkreis T\xc3\xbcbingen, Baden-W\xc3\xbcrttemberg, Deutschland", "boundingbox":["48.4949404","48.4950404","9.0402802","9.0403802"]}]'
    status_code = 200

    def json(self):
        return json.loads(self.content.decode())


class RequestMock:
    @staticmethod
    def get(url, params=None, data=None, headers=None):
        return ResponseMock()


class GeoFeature:

    @staticmethod
    def geofeatures_from_photon_result(result):
        geofeatures = []
        for feature in result["features"]:
            geojson = {}
            # Necessary features
            geojson['place_id'] = feature["properties"]["osm_id"]
            geojson['lat'] = feature["geometry"]["coordinates"][1]
            geojson['lon'] = feature["geometry"]["coordinates"][0]
            try:
                geojson['name'] = feature["properties"]["name"]
            except KeyError:
                geojson['name'] = feature["properties"]["osm_id"]

            optional_keys = ["housenumber", "street", "city", "postcode", "county", "countrycode"]
            for key in optional_keys:
                try:
                    geojson[key] = feature["properties"][key]
                except KeyError:
                    pass
            geofeatures.append(geojson)
        return geofeatures

    @staticmethod
    def geofeatures_from_nominatim_result(result):
        geofeatures = []
        for feature in result:
            geojson = {}
            if "name" in feature:
                geojson['name'] = feature["name"]
            else:
                geojson['name'] = feature["display_name"]
            geojson['place_id'] = feature["place_id"]
            geojson['lat'] = feature["lat"]
            geojson['lon'] = feature["lon"]
            geofeatures.append(geojson)
        return geofeatures


class GeoAPI:
    api_url = settings.GEOCODING_API_URL
    api_format = settings.GEOCODING_API_FORMAT
    assert api_format in ['nominatim', 'photon']

    # Set User-Agent headers as required by most usage policies (and it's the nice thing to do)
    headers = {
        'User-Agent': f"Notfellchen {nf_version}",
        'From': 'info@notfellchen.org'  # This is another valid field
    }

    def __init__(self, debug=False):
        # If debug mode is on, we replace the actual goecoding server with a cheap local mock
        # In order to do this without changing how we normally do things, we replace the requests library with our mock
        if debug:
            self.requests = RequestMock
        else:
            self.requests = requests

    def _get_raw_response(self, location_string):
        result = self.requests.get(self.api_url, {"q": location_string, "format": "jsonv2"}, headers=self.headers)
        return result.content

    def get_geojson_for_query(self, location_string, language="de"):
        try:
            if self.api_format == 'nominatim':
                logging.info(f"Querying nominatim instance for: {location_string} ({self.api_url})")
                result = self.requests.get(self.api_url,
                                           {"q": location_string,
                                            "format": "jsonv2"},
                                           headers=self.headers).json()
                geofeatures = GeoFeature.geofeatures_from_nominatim_result(result)
            elif self.api_format == 'photon':
                logging.info(f"Querying photon instance for: {location_string} ({self.api_url})")
                result = self.requests.get(self.api_url,
                                           {"q": location_string, "lang": language},
                                           headers=self.headers).json()
                geofeatures = GeoFeature.geofeatures_from_photon_result(result)
            else:
                raise NotImplementedError

        except Exception as e:
            logging.warning(f"Exception {e} when querying geocoding server")
            return None
        if len(geofeatures) == 0:
            logging.warning(f"Couldn't find a result for {location_string} when querying geocoding server")
            return None
        return geofeatures


class LocationProxy:
    """
    Location proxy is used as a precursor to the location model without the need to create unnecessary database objects
    """

    def __init__(self, location_string):
        """
        Creates the location proxy from the location string
        """
        self.geo_api = GeoAPI()
        geofeatures = self.geo_api.get_geojson_for_query(location_string)

        if geofeatures is None:
            raise ValueError
        result = geofeatures[0]
        self.name = result["name"]
        self.place_id = result["place_id"]
        self.latitude = result["lat"]
        self.longitude = result["lon"]
        optional_keys = ["housenumber", "street", "city", "postcode", "county", "countrycode"]
        for key in optional_keys:
            try:
                self.__setattr__(key, result[key])
            except KeyError:
                self.__setattr__(key, None)

    def __eq__(self, other):
        return self.place_id == other.place_id

    def __str__(self):
        return self.name

    @property
    def position(self):
        return (self.latitude, self.longitude)


if __name__ == "__main__":
    geo = GeoAPI(debug=False)
    print(calculate_distance_between_coordinates(('48.4949904', '9.040330235970146'), ("48.648333", "9.451111")))
