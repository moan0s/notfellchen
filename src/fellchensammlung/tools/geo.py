import requests
import json
from notfellchen import __version__ as nf_version


class ResponseMock:
    content = b'[{"place_id":138181499,"licence":"Data \xc2\xa9 OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright","osm_type":"relation","osm_id":1247237,"lat":"48.4949904","lon":"9.040330235970146","category":"boundary","type":"postal_code","place_rank":21, "importance":0.12006895017929346,"addresstype":"postcode","name":"72072","display_name":"72072, Derendingen, T\xc3\xbcbingen, Landkreis T\xc3\xbcbingen, Baden-W\xc3\xbcrttemberg, Deutschland", "boundingbox":["48.4949404","48.4950404","9.0402802","9.0403802"]}]'

    def json(self):
        return json.loads(self.content.decode())


class RequestMock:
    @staticmethod
    def get(url, params=None, data=None, headers=None):
        return ResponseMock()


class GeoAPI:
    def __init__(self, debug=True):
        self.api_url = "https://nominatim.openstreetmap.org/search"
        if debug:
            self.requests = RequestMock
        else:
            self.requests = requests

    def get_coordinates_from_postcode(self, postcode):
        headers = {
            'User-Agent': f"Notfellchen {nf_version}",
            'From': 'info@notfellchen.org'  # This is another valid field
        }
        result = self.requests.get(self.api_url, {"q": postcode, "format": "jsonv2"}, headers=headers).json()[0]
        return result["lat"], result["lon"]


if __name__ == "__main__":
    geo = GeoAPI(debug=True)
    print(geo.get_coordinates_from_postcode("72072"))
