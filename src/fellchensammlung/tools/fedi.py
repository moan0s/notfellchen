import logging
import requests
from django.template.loader import render_to_string

from fellchensammlung.models import SocialMediaPost, PlatformChoices
from notfellchen import settings


class FediClient:
    def __init__(self, access_token, api_base_url):
        """
        :param access_token: Your server API access token.
        :param api_base_url: The base URL of the Fediverse instance (e.g., 'https://gay-pirate-assassins.de').
        """
        self.access_token = access_token
        self.api_base_url = api_base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

    def upload_media(self, image_path, alt_text):
        """
        Uploads media (image) to the server and returns the media ID.
        :param image_path: Path to the image file to upload.
        :param alt_text: Description (alt text) for the image.
        :return: The media ID of the uploaded image.
        """

        media_endpoint = f'{self.api_base_url}/api/v2/media'

        with open(image_path, 'rb') as image_file:
            files = {
                'file': image_file,
                'description': (None, alt_text)
            }
            response = requests.post(media_endpoint, headers=self.headers, files=files)

            # Raise exception if upload fails
            response.raise_for_status()

        # Parse and return the media ID from the response
        media_id = response.json().get('id')
        return media_id

    def post_status(self, status, media_ids=None):
        """
        Posts a status to Mastodon with optional media.
        :param status: The text of the status to post.
        :param media_ids: A list of media IDs to attach to the status (optional).
        :return: The response from the Mastodon API.
        """
        status_endpoint = f'{self.api_base_url}/api/v1/statuses'

        payload = {
            'status': status,
            'media_ids[]': media_ids if media_ids else []
        }
        response = requests.post(status_endpoint, headers=self.headers, data=payload)

        # Raise exception if posting fails
        response.raise_for_status()

        return response.json()

    def post_status_with_images(self, status, images):
        """
        Uploads one or more image, then posts a status with that images and alt text.
        :param status: The text of the status.
        :param image_paths: The paths to the image file.
        :param alt_text: The alt text for the image.
        :return: The response from the Mastodon API.
        """
        media_ids = []
        for image in images:
            # Upload the image and get the media ID
            media_ids = self.upload_media(f"{settings.MEDIA_ROOT}/{image.image}", image.alt_text)

        # Post the status with the uploaded image's media ID
        return self.post_status(status, media_ids=media_ids)


def post_an_to_fedi(adoption_notice):
    client = FediClient(settings.fediverse_access_token, settings.fediverse_api_base_url)

    context = {"adoption_notice": adoption_notice}
    status_text = render_to_string("fellchensammlung/misc/fediverse/an-post.md", context)
    images = adoption_notice.get_photos()

    if images is not None:
        response = client.post_status_with_images(status_text, images)
    else:
        response = client.post_status(status_text)
    logging.info(response)
    post = SocialMediaPost.objects.create(adoption_notice=adoption_notice,
                                          platform=PlatformChoices.FEDIVERSE,
                                          url=response['url'], )
    return post
