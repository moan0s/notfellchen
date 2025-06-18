import argparse
import os
import requests
# TODO: consider using OSMPythonTools instead of requests or overpass library
from osmtogeojson import osmtogeojson
from tqdm import tqdm

DEFAULT_OSM_DATA_FILE = "export.geojson"
# Search area must be the official name, e.g. "Germany" is not a valid area name in Overpass API
# Consider instead finding & using the code within the query itself, e.g. "ISO3166-1"="DE"
DEFAULT_OVERPASS_SEARCH_AREA = "Deutschland" 


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Download animal shelter data from the Overpass API to the Notfellchen API.")
    parser.add_argument("--api-token", type=str, help="API token for authentication.")
    parser.add_argument("--area", type=str, help="Area to search for animal shelters (default: Deutschland).")
    parser.add_argument("--instance", type=str, help="API instance URL.")
    parser.add_argument("--data-file", type=str, help="Path to the GeoJSON file containing (only) animal shelters.")
    return parser.parse_args()


def get_config():
    """Get configuration from environment variables or command-line arguments."""
    args = parse_args()

    api_token = args.api_token or os.getenv("NOTFELLCHEN_API_TOKEN")
    # TODO: document new environment variable NOTFELLCHEN_AREA
    area = args.area or os.getenv("NOTFELLCHEN_AREA", DEFAULT_OVERPASS_SEARCH_AREA)
    instance = args.instance or os.getenv("NOTFELLCHEN_INSTANCE")
    data_file = args.data_file or os.getenv("NOTFELLCHEN_DATA_FILE", DEFAULT_OSM_DATA_FILE)

    if not api_token or not instance:
        raise ValueError("API token and instance URL must be provided via environment variables or CLI arguments.")

    return api_token, area, instance, data_file


def get_or_none(data, key):
    if key in data["properties"].keys():
        return data["properties"][key]
    else:
        return ""


def choose(keys, data, replace=False):
    for key in keys:
        if key in data.keys():
            if replace:
                return data[key].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            else:
                return data[key]
    return None


def add(value, platform):
    if value != "":
        if value.find(platform) == -1:
            return f"https://www.{platform}.com/{value}"
        else:
            return value
    else:
        return None


def https(value):
    if value is not None and value != "":
        value = value.replace("http://", "")
        if value.find("https") == -1:
            return f"https://{value}"
        else:
            return value
    else:
        return None


# TODO: take note of new get_overpass_result function which does the bulk of the new overpass query work
def get_overpass_result(area):
    """Build the Overpass query for fetching animal shelters in the specified area."""
    overpass_endpoint = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
        [out:json][timeout:25];
        area[name="{area}"]->.searchArea;
        nwr["amenity"="animal_shelter"](area.searchArea);
        out body;
        >;
        out skel qt;
        """
    r = requests.get(overpass_endpoint, params={'data': overpass_query})
    if r.status_code == 200:
        result = osmtogeojson.process_osm_json(r.json())
        return result


def main():
    api_token, area, instance, data_file = get_config()
    # Query shelters
    overpass_result = get_overpass_result(area)
    if overpass_result is None:
        print("Error: get_overpass_result returned None")
        return
    print(f"Response type: {type(overpass_result)}")
    print(f"Response content: {overpass_result}")

    # Set headers and endpoint
    endpoint = f"{instance}/api/organizations/"
    h = {'Authorization': f'Token {api_token}', "content-type": "application/json"}

    for idx, tierheim in tqdm(enumerate(overpass_result["features"])):

        if "name" not in tierheim["properties"].keys() or "addr:city" not in tierheim["properties"].keys():
            continue

        data = {"name": tierheim["properties"]["name"],
                "location_string": f"{get_or_none(tierheim, "addr:street")} {get_or_none(tierheim, "addr:housenumber")}, {get_or_none(tierheim, "addr:postcode")} {tierheim["properties"]["addr:city"]}",
                "phone_number": choose(("contact:phone", "phone"), tierheim["properties"], replace=True),
                "fediverse_profile": get_or_none(tierheim, "contact:mastodon"),
                "facebook": https(add(get_or_none(tierheim, "contact:facebook"), "facebook")),
                "instagram": https(add(get_or_none(tierheim, "contact:instagram"), "instagram")),
                "website": https(choose(("contact:website", "website"), tierheim["properties"])),
                "email": choose(("contact:email", "email"), tierheim["properties"]),
                "description": get_or_none(tierheim, "opening_hours"),
                "external_object_identifier": f"{tierheim["id"]}",
                "external_source_identifier": "OSM"
                }

        result = requests.post(endpoint, json=data, headers=h)

        if result.status_code != 201:
            print(f"{idx} {tierheim["properties"]["name"]}:{result.status_code} {result.json()}")


if __name__ == "__main__":
    main()
