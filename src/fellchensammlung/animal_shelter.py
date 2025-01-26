import json
import requests

OSM_DATA_FILE = "osm_data.geojson"
ENDPOINT = "https://test.notfellchen.org/api/organizations/"
HEADERS = {
    "Authorization": "API_KEY",
    "Content-Type": "application/json"
}


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


def send_to_api(data):
    # Send transformed data to the Notfellchen API.
    response = requests.post(ENDPOINT, headers=HEADERS, json=data)
    if response.status_code == 201:
        print(f"Success: Shelter '{data['name']}' uploaded.")
    elif response.status_code == 400:
        print(f"Error: Shelter '{data['name']}' already exists or invalid data.")
    else:
        print(f"Unexpected Error: {response.status_code} - {response.text}")
        raise ConnectionError


def main():
    # Step 1: Load OSM data
    osm_data = load_osm_data(OSM_DATA_FILE)

    # Step 2: Process each shelter and send it to the API
    for feature in osm_data.get("features", []):
        shelter_data = transform_osm_data(feature)
        send_to_api(shelter_data)

if __name__ == "__main__":
    main()
