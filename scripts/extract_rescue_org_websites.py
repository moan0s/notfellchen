import argparse
import csv
import os

import requests

OUTPUT_FILE = "export.csv"


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download animal shelter data from the Overpass API to the Notfellchen API.")
    parser.add_argument("--api-token", type=str, help="API token for authentication.")
    parser.add_argument("--instance", type=str, help="API instance URL.")
    parser.add_argument("--output-file", type=str, help="Path output file.")
    return parser.parse_args()


def get_config():
    """Get configuration from environment variables or command-line arguments."""
    args = parse_args()

    api_token = args.api_token or os.getenv("NOTFELLCHEN_API_TOKEN")
    instance = args.instance or os.getenv("NOTFELLCHEN_INSTANCE")
    output_file = args.output_file or OUTPUT_FILE

    return api_token, instance, output_file


def rat_specific_url_or_none(org):
    try:
        urls = org["species_specific_urls"]
        for url in urls:
            # 1 is the key for rats
            if url["species"] == 1:
                return url["url"]
        # Return none if no url for this species is found
        return None
    except KeyError:
        return None


def main():
    api_token, instance, output_file = get_config()

    # Set headers and endpoint
    endpoint = f"{instance}/api/organizations/"
    h = {'Authorization': f'Token {api_token}', "content-type": "application/json"}

    rescue_orgs_result = requests.get(endpoint, headers=h)

    with open(output_file, 'w') as csvfile:
        fieldnames = ['id', 'name', 'website', 'rat_specific_website']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for org in rescue_orgs_result.json():
            writer.writerow({'id': org["id"],
                             'name': org["name"],
                             'website': org["website"],
                             "rat_specific_website": rat_specific_url_or_none(org)})


if __name__ == "__main__":
    main()
