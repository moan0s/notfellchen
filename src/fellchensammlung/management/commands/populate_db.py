from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from fellchensammlung.models import *
from fellchensammlung import baker_recipes
from model_bakery import baker


class Command(BaseCommand):
    help = "Populates the database with test data"

    @staticmethod
    def populate_db():
        rat1 = baker.make_recipe(
            'fellchensammlung.rat'
        )
        rat2 = baker.make_recipe(
            'fellchensammlung.rat'
        )
        cat = baker.make_recipe(
            'fellchensammlung.cat'
        )
        rescue1 = baker.make_recipe(
            'fellchensammlung.rescue_org'
        )
        rescue2 = baker.make_recipe(
            'fellchensammlung.rescue_org'
        )

        baker.make(AdoptionNotice, name="Vermittung1", animals=[rat1, rat2], organization=rescue1)

        baker.make(AdoptionNotice, name="Vermittung2", animals=[cat], organization=rescue2)

        User.objects.create_user('test', password='foobar')
        User.objects.create_superuser(username="admin", password="admin")

    def handle(self, *args, **options):
        self.populate_db()
