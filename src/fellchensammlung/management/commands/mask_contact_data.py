from django.core.management import BaseCommand
from fellchensammlung.tools.admin import mask_organization_contact_data


class Command(BaseCommand):
    help = 'Mask e-mail addresses and phone numbers of organizations for testing purposes.'

    def add_arguments(self, parser):
        parser.add_argument("domain", type=str)

    def handle(self, *args, **options):
        domain = options["domain"]
        mask_organization_contact_data(domain)
