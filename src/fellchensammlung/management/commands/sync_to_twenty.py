from django.core.management import BaseCommand
from tqdm import tqdm

from fellchensammlung.models import RescueOrganization
from fellchensammlung.tools.twenty import sync_rescue_org_to_twenty


class Command(BaseCommand):
    help = 'Send rescue organizations as companies to twenty'

    def add_arguments(self, parser):
        parser.add_argument("base_url", type=str)
        parser.add_argument("token", type=str)

    def handle(self, *args, **options):
        base_url = options["base_url"]
        token = options["token"]
        for rescue_org in tqdm(RescueOrganization.objects.all()):
            sync_rescue_org_to_twenty(rescue_org, base_url, token)
