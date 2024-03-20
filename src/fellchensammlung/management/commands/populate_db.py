from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from fellchensammlung.models import *
from fellchensammlung import baker_recipes
from model_bakery import baker


class Command(BaseCommand):
    help = "Populates the database with test data"

    @staticmethod
    def populate_db():
        rescue1 = baker.make_recipe(
            'fellchensammlung.rescue_org'
        )
        rescue2 = baker.make_recipe(
            'fellchensammlung.rescue_org'
        )

        adoption1 = baker.make(AdoptionNotice, name="Vermittung1", organization=rescue1)

        adoption2 = baker.make(AdoptionNotice, name="Vermittung2",  organization=rescue2)

        cat = baker.make(Species, name="Katze")
        rat = baker.make(Species, name="Farbratte")

        rat1 = baker.make(Animal, name="Rat1", adoption_notice=adoption1, species=rat)
        rat2 = baker.make(Animal, name="Rat2", adoption_notice=adoption1, species=rat)
        cat1 = baker.make(Animal, name="Cat1", adoption_notice=adoption2, species=cat)

        rule1 = baker.make(Rule, title="Be excellent ot each other", rule_text="This is **markdown**")
        rule2 = baker.make(Rule,
                           title="Keep al least the minimum number of animals for species",
                           rule_text="This is not markdown")

        User.objects.create_user('test', password='foobar')
        User.objects.create_superuser(username="admin", password="admin")

    def handle(self, *args, **options):
        self.populate_db()
