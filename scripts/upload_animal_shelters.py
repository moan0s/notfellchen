import argparse
import json
import os
import requests
from tqdm import tqdm

DEFAULT_OSM_DATA_FILE = "export.geojson"


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Upload animal shelter data to the Notfellchen API.")
    parser.add_argument("--api-token", type=str, help="API token for authentication.")
    parser.add_argument("--instance", type=str, help="API instance URL.")
    parser.add_argument("--data-file", type=str, help="Path to the GeoJSON file containing (only) animal shelters.")
    return parser.parse_args()


def get_config():
    """Get configuration from environment variables or command-line arguments."""
    args = parse_args()

    api_token = args.api_token or os.getenv("NOTFELLCHEN_API_TOKEN")
    instance = args.instance or os.getenv("NOTFELLCHEN_INSTANCE")
    data_file = args.data_file or os.getenv("NOTFELLCHEN_DATA_FILE", DEFAULT_OSM_DATA_FILE)

    if not api_token or not instance:
        raise ValueError("API token and instance URL must be provided via environment variables or CLI arguments.")

    return api_token, instance, data_file


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


def main():
    api_token, instance, data_file = get_config()
    # Set headers and endpoint
    endpoint = f"{instance}/api/organizations/"
    h = {'Authorization': f'Token {api_token}', "content-type": "application/json"}

    with open(data_file, encoding="utf8") as f:
        d = json.load(f)

    for idx, tierheim in tqdm(enumerate(d["features"])):
        # Check if data is low quality
        if "name" not in tierheim["properties"].keys() or "addr:city" not in tierheim["properties"].keys():
            continue

        # Check if rescue organization exits
        search_data = {"external_source_identifier": "OSM",
                       "external_object_identifier": f"{tierheim["id"]}"}
        search_result = requests.get(f"{instance}/api/organizations", json=search_data, headers=h)
        if search_result.status_code == 200:
            print(f"{tierheim["properties"]["name"]} already exists.")
            continue

        location_data = {
            "place_id": tierheim["id"],
            "latitude": tierheim["geometry"]["coordinates"][0][0][0],
            "longitude": tierheim["geometry"]["coordinates"][0][0][1],
            "name": tierheim["properties"]["name"],
            "city": tierheim["properties"]["addr:city"],
            "housenumber": get_or_none(tierheim, "addr:housenumber"),
            "postcode": get_or_none(tierheim, "addr:postcode"),
            "street": get_or_none(tierheim, "addr:street"),
            "countrycode": get_or_none(tierheim, "addr:country"),
        }

        location_result = requests.post(f"{instance}/api/locations/", json=location_data, headers=h)

        if location_result.status_code != 201:
            print(
                f"{idx} Location for {tierheim["properties"]["name"]}:{location_result.status_code} {location_result.json()} not created")
            exit()

        data = {"name": tierheim["properties"]["name"],
                "location": json.loads(location_result.content)["id"],
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
