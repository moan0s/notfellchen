from rest_framework.renderers import BaseRenderer
import json


class GeoJSONRenderer(BaseRenderer):
    media_type = 'application/json'
    format = 'geojson'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        features = []
        for item in data:
            coords = item["coordinates"]
            if coords:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    },
                    "properties": {
                        k: v for k, v in item.items()
                    },
                    "id": f"adoptionnotice/{item['id']}"
                }
                features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "generator": "notfellchen",
            "features": features
        }
        return json.dumps(geojson)
