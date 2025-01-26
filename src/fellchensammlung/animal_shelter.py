import argparse
import json
import os

import requests

DEFAULT_OSM_DATA_FILE = "osm_data.geojson"


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


def load_osm_data(file_path):
    """Load OSM data from a GeoJSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def load_osm_data(file_path):
    #Load OSM data from a GeoJSON file.
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def transform_osm_data(feature):
    #Transform a single OSM feature into the API payload format
    prop = feature.get("properties", {})
    geometry = feature.get("geometry", {})

    return {
        "name": prop.get("name", "Unnamed Shelter"),
        "phone": prop.get("phone"),
        "website": prop.get("website"),
        "opening_hours": prop.get("opening_hours"),
        "email": prop.get("email"),
        "location_string": f'{prop.get("addr:street", "")} {prop.get("addr:housenumber", "")} {prop.get("addr:postcode", "")} {prop.get("addr:city", "")}',
        "external_object_id": prop.get("@id"),
        "external_source_id": "OSM"
    }


def send_to_api(data, endpoint, headers):
    # Send transformed data to the Notfellchen API.
    response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Success: Shelter '{data['name']}' uploaded.")
    elif response.status_code == 400:
        print(f"Error: Shelter '{data['name']}' already exists or invalid data.")
    else:
        print(f"Unexpected Error: {response.status_code} - {response.text}")
        raise ConnectionError


def main():
    # Get configuration
    api_token, instance, data_file = get_config()

    # Set headers and endpoint
    endpoint = f"{instance}/api/organizations/"
    headers = {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Load OSM data
    osm_data = load_osm_data(data_file)

    # Step 2: Process each shelter and send it to the API
    for feature in osm_data.get("features", []):
        shelter_data = transform_osm_data(feature)
        send_to_api(shelter_data, endpoint, headers)


if __name__ == "__main__":
    main()
