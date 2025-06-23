from django.core.management import BaseCommand

from fellchensammlung.tools.admin import export_orgs_as_vcf


class Command(BaseCommand):
    help = 'Export organizations with phone number as contacts in vcf format'

    def handle(self, *args, **options):
        export_orgs_as_vcf()

