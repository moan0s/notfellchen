import argparse
import json
import os
from types import SimpleNamespace

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


def get_center_coordinates(geometry):
    """
    Given a GeoJSON geometry dict, return (longitude, latitude)

    If a shape, calculate the center, else reurn the point
    """
    geom_type = geometry["type"]
    coordinates = geometry["coordinates"]

    if geom_type == "Point":
        return coordinates[0], coordinates[1]

    elif geom_type == "LineString":
        return calc_coordinate_center(coordinates)

    elif geom_type == "Polygon":
        outer_ring = coordinates[0]
        return calc_coordinate_center(outer_ring)

    else:
        raise ValueError(f"Unsupported geometry type: {geom_type}")


def calc_coordinate_center(coordinates):
    """
    Calculates the center as the arithmetic mean of the list of coordinates.

    Not perfect because earth is a sphere (citation needed) but good enough.
    """
    if not coordinates:
        return None, None

    lon_sum = 0.0
    lat_sum = 0.0
    count = 0

    for lon, lat in coordinates:
        lon_sum += lon
        lat_sum += lat
        count += 1

    return lon_sum / count, lat_sum / count


def add_if_available(base_data, keys, result):
    # Loads the data into the org if available
    for key in keys:
        if getattr(base_data, key) is not None:
            result[key] = getattr(base_data, key)
    return result


def main():
    api_token, instance, data_file = get_config()
    # Set headers and endpoint
    endpoint = f"{instance}/api/organizations/"
    h = {'Authorization': f'Token {api_token}', "content-type": "application/json"}

    with open(data_file, encoding="utf8") as f:
        d = json.load(f)

    skipped_low_quality = 0

    tierheime = d["features"]

    for idx, tierheim in enumerate(tierheime):
        # Check if data is low quality
        if "name" not in tierheim["properties"].keys() or "addr:city" not in tierheim["properties"].keys():
            skipped_low_quality = skipped_low_quality + 1
            continue

        # Load TH data in for easier accessing
        th_data = SimpleNamespace(
            name=tierheim["properties"]["name"],
            email=choose(("contact:email", "email"), tierheim["properties"]),
            phone_number=choose(("contact:phone", "phone"), tierheim["properties"], replace=True),
            fediverse_profile=get_or_none(tierheim, "contact:mastodon"),
            facebook=https(add(get_or_none(tierheim, "contact:facebook"), "facebook")),
            instagram=https(add(get_or_none(tierheim, "contact:instagram"), "instagram")),
            website=https(choose(("contact:website", "website"), tierheim["properties"])),
            description=get_or_none(tierheim, "opening_hours"),
            external_object_identifier=tierheim["id"],
            EXTERNAL_SOURCE_IDENTIFIER="OSM",
        )

        # Define here for later
        optional_data = ["email", "phone_number", "website", "description", "fediverse_profile", "facebook",
                         "instagram"]

        # Check if rescue organization exits
        search_data = {"external_source_identifier": "OSM",
                       "external_object_identifier": f"{tierheim["id"]}"}
        search_result = requests.get(f"{instance}/api/organizations", params=search_data, headers=h)
        if search_result.status_code == 200:
            org_id = search_result.json()[0]["id"]
            print(f"{th_data.name} already exists as ID {org_id}.")
            org_patch_data = {"id": org_id,
                              "name": th_data.name}

            add_if_available(th_data, optional_data, org_patch_data)

            result = requests.patch(endpoint, json=org_patch_data, headers=h)
            if result.status_code != 200:
                print(f"Updating {tierheim['properties']['name']} failed:{result.status_code} {result.json()}")
                exit()
            continue

        location_data = {
            "place_id": tierheim["id"],
            "longitude": get_center_coordinates(tierheim["geometry"])[0],
            "latitude": get_center_coordinates(tierheim["geometry"])[1],
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

        org_data = {"name": tierheim["properties"]["name"],
                    "location": location_result.json()["id"],
                    "external_object_identifier": f"{tierheim["id"]}",
                    "external_source_identifier": "OSM"
                    }

        add_if_available(th_data, optional_data, org_data)

        result = requests.post(endpoint, json=org_data, headers=h)

        if result.status_code != 201:
            print(f"{idx} {tierheim["properties"]["name"]} failed:{result.status_code} {result.json()}")
            exit(1)
        else:
            print(f"{idx} - {json.loads(result.content)["id"]} {tierheim["properties"]["name"]} created")

    print(f"{skipped_low_quality} datapoints skipped for low quality ({100*skipped_low_quality / len(tierheime):.2}%)")


if __name__ == "__main__":
    main()
