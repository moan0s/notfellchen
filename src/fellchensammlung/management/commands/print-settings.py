from django.core.management import BaseCommand

from notfellchen import settings


class Command(BaseCommand):
    help = 'Print the current settings'

    def handle(self, *args, **options):
        for key in settings.__dir__():
            if key.startswith("_") or key == "SECRET_KEY":
                continue
            print(f"{key} = {getattr(settings, key)}")
